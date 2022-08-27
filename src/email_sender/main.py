"""
Модуль содержит основную логику работы сервиса.
Стоит пояснить что вообще делает email_sender:

Его задача принимать сообщение из очереди
(в сообщении будет вся нужная ему информация)
и отправлять письмо.
"""
import asyncio
import logging
from logging import config as logging_config

from config.logging_settings import LOGGING
from config.settings import config
from db.message_brokers.rabbit_message_broker import message_broker_factory
from db.storage import orm_factory
from email_sender.callback import callback  # type: ignore
from email_sender.models.log import log_names


async def startup() -> None:

    """Функция для действий во время старта приложения."""

    await message_broker_factory.idempotency_startup()
    await orm_factory.db.start()
    logger.info(log_names.info.started, 'email sender')


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
