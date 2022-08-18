"""
Модуль содержит класс с брокером сообщений.

Архитектура Rabbit такая:

Есть очередь, в которую попадают все вновь приходящие message — queue_waiting_depart.
Есть обменник для этой очереди — exchange_incoming.

По истечению expiration в очереди queue_waiting_depart message отправляются в сортирующий обменник — exchange_sorter.
В обменнике exchange_sorter message перенаправляются в очереди с одноименными названиями routing_key.
Иными словами сортировка такая: routing_key == queue_name

В этой очереди message дожидается пока её схватит consumer.
Если consumer что-то не смог сделать с сообщением
(иными словами не сказал basic_ack) — message отправляется в обменник exchange_retry,
а от туда сразу в очередь queue_waiting_retry.

В очереди queue_waiting_retry установлен аргумент x-message-ttl,
по истечению этого времени message отправится назад в exchange_sorter и цикл повторится.

Соответственно на совести разработчика следить за кол-вом таких итераций и,
если их кол-во превысит max_retry_count — дропить message, уведомляя об этом из логгера.
"""
import asyncio
from typing import Optional, Union, Callable

import aio_pika
from aio_pika import Message, DeliveryMode, ExchangeType
from aio_pika.abc import AbstractRobustConnection, AbstractIncomingMessage, \
    AbstractChannel, AbstractQueue
from pamqp.commands import Basic

from config.settings import config
from db.message_brokers.abstract_classes import AbstractMessageBroker


class RabbitMessageBroker(AbstractMessageBroker):

    """Класс с интерфейсом брокера сообщений RabbitMQ."""

    def __init__(self) -> None:
        """Конструктор."""
        self.host = config.rabbit_mq.host
        self.port = config.rabbit_mq.port
        self.login = config.rabbit_mq.login
        self.password = config.rabbit_mq.password

    async def consume(self, queue_name: str, callback: Callable) -> None:
        """
        Метод обрабатывает сообщения функцией callback из очереди с названием queue_name.

        Args:
            queue_name: название очереди, из которой хотим получить данные
            callback: функция, которая будет обрабатывать сообщения
        """
        connection = await self._get_connect()
        try:
            running_loop = asyncio.get_running_loop()
            channel = await connection.channel()
            queue = await self._create_alive_queue(queue_name=queue_name, channel=channel)
            iterator = queue.iterator()
            await iterator.consume()

            async for message in iterator:
                running_loop.create_task(callback(message))

        finally:  # Даже если украинские националисты будут под москвой мы всё равно закроем соединение. :)
            await connection.close()

    async def publish(
        self,
        message_body: bytes,
        queue_name: str,
        message_headers: Optional[dict] = None,
        delay: Union[int, float] = 0
    ) -> Union[Basic.Ack, Basic.Nack, Basic.Reject, None]:
        """
        Метод складывает сообщение в очередь.

        Args:
            message_body: содержимое сообщения
            delay: ttl сообщения, указывается в секундах (сколько секунд подождать прежде, чем отправить)
            queue_name: название очереди, в которую нужно отправить сообщение
            message_headers: заголовок сообщения (сюда нужно вставить x-request-id)

        Returns:
            Вернёт ответ на вопрос была ли запись успешно добавлена
        """
        connection = await self._get_connect()
        try:
            channel = await connection.channel()

            exchange_incoming = await channel.declare_exchange(
                name=config.rabbit_mq.exchange_incoming,
                type=ExchangeType.FANOUT,
                durable=True
            )

            message = Message(
                headers=message_headers or {},
                body=message_body,
                delivery_mode=DeliveryMode.PERSISTENT,
                expiration=delay
            )

            await self._create_alive_queue(queue_name=queue_name, channel=channel)
            return await exchange_incoming.publish(message=message, routing_key=queue_name)
        finally:  # Даже если метеорит упадёт на землю мы всё равно закроем соединение. :)
            await connection.close()

    async def idempotency_startup(self) -> None:
        """
        Метод для конфигурации базовой архитектуры RabbitMQ.
        Использовать ОДИН раз при старте сервиса.

        Можно конечно и больше,
        но этот метод все действие выполнит только один раз,
        следовательно, никакого резона вызывать его более одного раза нет.
        """
        connection = await self._get_connect()
        try:
            channel = await connection.channel()

            # Обменник, принимающий все входящие в rabbit сообщения.
            exchange_incoming = await channel.declare_exchange(
                name=config.rabbit_mq.exchange_incoming,
                type=ExchangeType.FANOUT,
                durable=True
            )

            # Обменник, сортирующий сообщения и распределяющий их в нужные «живые» очереди, исходя из routing_key.
            exchange_sorter = await channel.declare_exchange(  # noqa: F841
                name=config.rabbit_mq.exchange_sorter,
                type=ExchangeType.DIRECT,
                durable=True
            )

            # Обменник, доставляющий сообщения во временное хранилище,
            # если попытка что-то сделать с сообщением не удалась.
            exchange_retry = await channel.declare_exchange(
                name=config.rabbit_mq.exchange_retry,
                type=ExchangeType.FANOUT,
                durable=True
            )

            # Базовая очередь, в которую будут поступать все сообщения.
            # По истечению ttl (может быть и ttl=0) отправляет сообщения в соответствующую routing_key очередь.
            # С помощью такой архитектуры мы можем создавать отложенные сообщения,
            # не прибегая к дополнительным инструментам (консистентно).
            queue_waiting_depart = await channel.declare_queue(
                name=config.rabbit_mq.queue_waiting_depart,
                durable=True,
                arguments={
                    'x-dead-letter-exchange': config.rabbit_mq.exchange_sorter
                }
            )

            # Очередь, где будут храниться все сообщения, которые не удалось обработать.
            # Они будут лежать в очереди определённое время (x-message-ttl).
            # По истечению этого времени будет вновь попытка отправить сообщение в «живую» очередь.
            queue_waiting_retry = await channel.declare_queue(
                name=config.rabbit_mq.queue_waiting_retry,
                durable=True,
                arguments={
                    'x-dead-letter-exchange': config.rabbit_mq.exchange_sorter,
                    'x-message-ttl': config.rabbit_mq.default_message_ttl_ms
                }
            )
            await queue_waiting_depart.bind(exchange_incoming)
            await queue_waiting_retry.bind(exchange_retry)
        finally:
            await connection.close()

    async def _create_alive_queue(self, queue_name: str, channel: AbstractChannel) -> AbstractQueue:
        """
        Внутренний метод для создания «живой» очереди и привязки её к сортирующему обменнику.

        Под живой очередью мы понимаем очередь, из которой consumer будет выкусывать данные.

        Args:
            queue_name: название очереди
            channel: канал

        Returns:
            Вернёт созданную очередь и обменник.
        """

        queue = await channel.declare_queue(
            name=queue_name,
            durable=True,
            arguments={
                'x-dead-letter-exchange': config.rabbit_mq.exchange_retry
            }
        )
        await queue.bind(config.rabbit_mq.exchange_sorter, routing_key=queue_name)
        return queue

    async def _get_connect(self) -> AbstractRobustConnection:
        """
        Внутренний метод класса (нужен для создания соединения).

        Returns:
            Вернёт соединение с БД.
        """
        return await aio_pika.connect_robust(
            host=self.host,
            port=self.port,
            login=self.login.get_secret_value(),
            password=self.password.get_secret_value()
        )


message_broker_factory = RabbitMessageBroker()


# Отсюда и ниже примеры, их нужно удалить после того, как станет всё ясно.
# Я просто оставила их тут, что бы было удобнее ориентироваться в интерфейсе класса.

async def callback(message: AbstractIncomingMessage) -> None:  # noqa: D103
    if message.info()['headers']['x-death'][0]['count'] + 1 > config.rabbit_mq.max_retry_count:
        print(message.body)  # noqa: WPS421
        await message.ack()
    else:
        print('Ждите', message.info()['headers']['x-death'][0]['count'])  # noqa: WPS421
        await message.reject()


async def quick_start() -> None:
    """Функция для быстрого знакомства с интерфейсом."""
    await message_broker_factory.idempotency_startup()
    queue_name = 'queue_alive'

    for i in range(5):
        message_body = f'message {i}'.encode()
        await message_broker_factory.publish(
            message_body=message_body,
            queue_name=queue_name,
            message_headers={'x-request-id': 'wwwwww'}
        )
    await message_broker_factory.consume(queue_name=queue_name, callback=callback)


if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(quick_start())
