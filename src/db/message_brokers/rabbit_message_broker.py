import asyncio
from functools import wraps
from random import randint
from time import time

import aio_pika
import aioredis
import orjson

# from config.settings import config

#
# async def callback(ch, method, properties, body):
#     print(body)
#     ch.basic_ack(delivery_tag=method.delivery_tag)


class RabbitMessageBroker:

    async def get_1(self, queue_name):
        connection = await aio_pika.connect_robust(
            # host=config.rabbit_mq.host,
            # port=config.rabbit_mq.port,
            # login=config.rabbit_mq.login.get_secret_value(),
            # password=config.rabbit_mq.password.get_secret_value(),
            "amqp://guest:guest@127.0.0.1/",
            loop=asyncio.get_running_loop()
        )

        await connection.connect()
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name, durable=True)
        iterator = queue.iterator()
        await iterator.consume()
        return iterator


    async def get(self, queue_name):

        connection = await aio_pika.connect_robust(
            # host=config.rabbit_mq.host,
            # port=config.rabbit_mq.port,
            # login=config.rabbit_mq.login.get_secret_value(),
            # password=config.rabbit_mq.password.get_secret_value(),
            "amqp://guest:guest@127.0.0.1/",
            loop=asyncio.get_running_loop()
        )

        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(queue_name, durable=True)

            async with queue.iterator() as queue_iterator:
                async for message in queue_iterator:
                    print(message.body.decode(), message.info()['delivery_tag'], message.info()['redelivered'])
                    # if '1' in message.body.decode():
                    #     await message.reject(requeue=True)

                    # else:
                    await asyncio.sleep(3)
                    await message.ack()

            #         async with message.process(ignore_processed=True):
            #             # await message.ack()
            #             print(message.body.decode(), message.info()['delivery_tag'], message.info()['redelivered'])
            #             # if '1' in message.body.decode():
            #             #     await message.reject(requeue=True)
            #             # else:
            #             #     await message.ack()
            #             await asyncio.sleep(3)
            #             await message.ack()

                        # task = func(redis_conn, message.body.decode(), start_time)
                        # loop.create_task(task)

                        # await message.ack()
                        # message.
                # return queue_iterator

    def put(self):
        ...


message_broker_factory = RabbitMessageBroker()


async def main():
    await callback()
    # await asyncio.gather(task('queue_simple_1'))


async def func(redis_conn, message_body, start_time):
    print(message_body)
    cus_time = time() - start_time
    await asyncio.sleep(randint(10, 80) / 1000)
    # await asyncio.sleep(3)
    await redis_conn.set(orjson.dumps(cus_time), orjson.dumps(message_body))


async def callback():
    data_from_consumer = await message_broker_factory.get_1('queue_simple_3')
    async for message in data_from_consumer:
        print(message.body.decode(), message.info()['delivery_tag'], message.info()['redelivered'])
        await asyncio.sleep(3)
        await message.ack()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
