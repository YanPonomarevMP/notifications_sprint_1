"""Модуль содержит класс с брокером сообщений."""
import asyncio
from typing import Optional

import aio_pika
from aio_pika import Message, DeliveryMode, ExchangeType
from aio_pika.abc import AbstractRobustConnection, AbstractQueueIterator

from config.app_settings import config
from db.message_brokers.abstract_classes import AbstractMessageBroker


class RabbitMessageBroker(AbstractMessageBroker):

    """Класс с интерфейсом брокера сообщений RabbitMQ."""

    def __init__(self) -> None:
        """Конструктор."""
        self.host = config.rabbit_mq.host
        self.port = config.rabbit_mq.port
        self.login = config.rabbit_mq.login
        self.password = config.rabbit_mq.password

    async def get(self, queue_name: str) -> AbstractQueueIterator:
        """
        Метод достаёт сообщения (возвращает итерируемый объект) из очереди с названием queue_name.

        Args:
            queue_name: название очереди, из которой хотим получить данные

        Returns:
            Вернёт асинхронный итератор.
        """
        connection = await self._get_connect()
        channel = await connection.channel()
        queue = await channel.declare_queue(name=queue_name, durable=True)
        iterator = queue.iterator()
        await iterator.consume()  # Инициируем работу итератора, т.к. он нам нужен уже работающий.
        return iterator

    async def put(
        self,
        message_body: bytes,
        queue_name: str,
        exchange_name: str,
        message_headers: Optional[dict] = None,
        expiration: int = config.rabbit_mq.message.expiration
    ) -> None:
        """
        Метод складывает сообщение в очередь.

        Args:
            message_body: содержимое сообщения
            expiration: ttl сообщения, указывается в миллисекундах
            queue_name: название очереди, в которую нужно отправить сообщение
            exchange_name: название обменника
            message_headers: заголовок сообщения (сюда нужно вставить x-request-id)
        """
        connection = await self._get_connect()
        channel = await connection.channel()
        exchange = await channel.declare_exchange(name=exchange_name, type=ExchangeType.FANOUT)
        message = Message(
            headers=message_headers or {},
            body=message_body,
            delivery_mode=DeliveryMode.PERSISTENT,
            expiration=expiration
        )

        await exchange.publish(message=message, routing_key=queue_name)
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


message_broker_factory: AbstractMessageBroker = RabbitMessageBroker()


async def callback() -> None:
    """
    Функция демонстрирует возможности класса.
    В данном случае демонстрация работы функции по выкусу и обработке данных.
    """
    data_from_consumer = await message_broker_factory.get('queue_1')
    async for message in data_from_consumer:
        print('выкусили', message.body.decode())  # noqa: WPS421
        await asyncio.sleep(3)
        await message.ack()


async def create_data() -> None:
    """
    Функция демонстрирует возможности класса.
    В данном случае демонстрация работы функции по вставке данных.
    """
    expiration = 5 * 1000  # 5 минут.
    queue_name = 'queue_1'
    exchange_name = 'exc_queue_1'

    for i in range(1, 6):
        message_body = f'message № {i}'
        await message_broker_factory.put(
            message_body=message_body.encode(),
            expiration=expiration,
            queue_name=queue_name,
            exchange_name=exchange_name
        )
        print('записали', message_body)  # noqa: WPS421


async def main() -> None:
    """Две функции-демонстратора в одном."""
    await create_data()
    await callback()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
