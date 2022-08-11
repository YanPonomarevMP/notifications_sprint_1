import asyncio

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
        await iterator.consume()  # Инициируем работу итератора.
        return iterator

    async def put(
        self,
        message_body: bytes,
        expiration: int,
        queue_name: str,
        exchange_name: str
    ):
        connection = await self._get_connect()
        channel = await connection.channel()
        exchange = await channel.declare_exchange(name=exchange_name, type=ExchangeType.FANOUT)
        message = Message(
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
            password=self.password.get_secret_value(),
            loop=asyncio.get_running_loop()
        )
        await connection.connect()
        return connection


message_broker_factory = RabbitMessageBroker()


async def main():
    await callback()


async def callback():
    data_from_consumer = await message_broker_factory.get('queue_simple_3')
    async for message in data_from_consumer:
        print(message.body.decode(), message.info()['delivery_tag'], message.info()['redelivered'])
        await asyncio.sleep(3)
        await message.ack()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
