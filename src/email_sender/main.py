import asyncio
import logging
from logging import config as logging_config

from aio_pika.abc import AbstractIncomingMessage

from config.logging_settings import LOGGING
from config.settings import config
from db.message_brokers.rabbit_message_broker import message_broker_factory
from db.storage import orm_factory
from email_sender.models.message_data import MessageData


async def callback(message: AbstractIncomingMessage):
    header = message.info()
    body = message.body.decode()
    message_data = MessageData(
        x_request_id=header,
        count_retry=header,
        notification_id=message.body,
        html=message.body,
        from_user=message.body,
        to_user=message.body,
        subject=message.body
    )
    print(message_data)
    return await message.ack()


async def startup() -> None:

    """Функция для действий во время старта приложения."""

    await message_broker_factory.idempotency_startup()
    await orm_factory.db.start()


async def shutdown() -> None:

    """Функция для действий во время завершения работы приложения."""

    await orm_factory.db.stop()


async def main() -> None:

    """Функция, запускающая всё приложение."""

    await startup()
    await message_broker_factory.consume(
        queue_name=config.rabbit_mq.queue_formatted_single_messages,
        callback=callback
    )
    await shutdown()


logging_config.dictConfig(LOGGING)
logger = logging.getLogger('email_sender')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
