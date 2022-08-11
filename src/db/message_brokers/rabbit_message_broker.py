import asyncio
from typing import Optional

import aio_pika
from aio_pika import Message, DeliveryMode, ExchangeType
from aio_pika.abc import AbstractRobustConnection

from config.settings import config


class RabbitMessageBroker:

    def __init__(self):
        self.host = config.rabbit_mq.host
        self.port = config.rabbit_mq.port
        self.login = config.rabbit_mq.login
        self.password = config.rabbit_mq.password

    async def get(self, queue_name):
        connection = await self._get_connect()
        channel = await connection.channel()
        queue = await channel.declare_queue(name=queue_name, durable=True)
        iterator = queue.iterator()
        await iterator.consume()  # Инициируем работу итератора, т.к. он нам нужен уже работающий.
        return iterator

    async def put(
        self,
        message_body: bytes,
        expiration: int,
        queue_name: str,
        exchange_name: str,
        message_headers: Optional[dict] = None
    ):
        connection = await self._get_connect()
        channel = await connection.channel()
        exchange = await channel.declare_exchange(name=exchange_name, type=ExchangeType.FANOUT)
        message = Message(
            headers=message_headers or {},
            body=message_body,
            delivery_mode=DeliveryMode.PERSISTENT,
            expiration=expiration
        )

        await exchange.publish(message, routing_key=queue_name)

    async def _get_connect(self) -> AbstractRobustConnection:
        connection = await aio_pika.connect_robust(
            host=self.host,
            port=self.port,
            login=self.login.get_secret_value(),
            password=self.password.get_secret_value()
        )
        return connection


message_broker_factory = RabbitMessageBroker()


async def callback():
    data_from_consumer = await message_broker_factory.get('queue_1')
    async for message in data_from_consumer:
        print(message.body.decode(), message.info()['delivery_tag'], message.info()['redelivered'])
        await asyncio.sleep(3)
        await message.ack()


async def create_data():

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
        print('записали', message_body)


async def main():
    await create_data()
    await callback()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
