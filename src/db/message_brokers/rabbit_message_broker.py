"""Модуль содержит класс с брокером сообщений."""
import asyncio
from typing import Optional, Union, Callable

import aio_pika
from aio_pika import Message, DeliveryMode, ExchangeType
from aio_pika.abc import AbstractRobustConnection, AbstractIncomingMessage

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
            channel = await connection.channel()
            queue = await channel.declare_queue(name=queue_name, durable=True)
            iterator = queue.iterator()
            await iterator.consume()

            async for message in iterator:
                await callback(message)

        finally:  # Даже если украинские националисты будут под москвой мы всё равно закроем соединение. :)
            await connection.close()

    async def publish(
        self,
        message_body: bytes,
        queue_name: str,
        exchange_name: str,
        message_headers: Optional[dict] = None,
        expiration: Optional[Union[int, float]] = None
    ) -> None:
        """
        Метод складывает сообщение в очередь.

        Args:
            message_body: содержимое сообщения
            expiration: ttl сообщения, указывается в секундах
            queue_name: название очереди, в которую нужно отправить сообщение
            exchange_name: название обменника
            message_headers: заголовок сообщения (сюда нужно вставить x-request-id)
        """
        connection = await self._get_connect()
        try:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(name=exchange_name, type=ExchangeType.FANOUT)
            message = Message(
                headers=message_headers or {},
                body=message_body,
                delivery_mode=DeliveryMode.PERSISTENT,
                expiration=expiration
            )

            await exchange.publish(message=message, routing_key=queue_name)
        finally:  # Даже если метеорит упадёт на землю мы всё равно закроем соединение. :)
            await connection.close()

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


async def on_message(message: AbstractIncomingMessage) -> None:
    """
    Функция демонстрирует работу обработчика сообщений из очереди.

    По задумке message_broker_factory.consume будет получать на вход название очереди и функцию.
    Эта функция и будет обрабатывать сообщения (как показано ниже в коде).

    Если вдруг потребуются доп. аргументы (что угодно кроме message) — всегда можно написать замыкание. :)

    Args:
        message: сообщение из очереди
    """
    print(f'Привет из функции-обработчика! Содержимое сообщения: {message.body.decode()}')  # noqa: WPS421, WPS237
    await asyncio.sleep(3)  # Любая логика
    await message.ack()  # Обязательно проставить галочку о том, что всё ок.


async def main() -> None:
    """Функция «Quick Start» (очередь и обменник предварительно нужно создать)."""
    for i in range(3):
        await message_broker_factory.publish(
            message_body=f'Какая-то byte строка, которую мы хотим записать {i}'.encode(),
            expiration=10,
            queue_name='queue_test',
            exchange_name='exc_queue_test'
        )
    await message_broker_factory.consume(queue_name='queue_test', callback=on_message)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
