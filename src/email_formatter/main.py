"""
Модуль содержит основную логику работы сервиса.
Стоит пояснить что вообще делает email_formatter:

Его задача принимать сообщение из одной очереди, форматировать (рендерить HTML шаблон) и отправлять в другую очередь.
Помимо самого HTML он еще должен найти адресата (его почту) в Auth сервисе и тоже отправить в очередь.
"""
import asyncio
import logging
from logging import config as logging_config

import aiohttp

from config.logging_settings import LOGGING
from config.settings import config
from db.message_brokers.rabbit_message_broker import message_broker_factory
from db.storage import orm_factory
from email_formatter.callback import callback  # type: ignore
from email_formatter.models.log import log_names
from utils import aiohttp_session


async def startup() -> None:

    """Функция для действий во время старта приложения."""

    headers = {'Authorization': config.auth_api.access_token.get_secret_value()}
    aiohttp_session.session = aiohttp.ClientSession(headers=headers)
    await message_broker_factory.idempotency_startup()
    await orm_factory.db.start()
    logger.info(log_names.info.started, 'formatter handler')


async def shutdown() -> None:

    """Функция для действий во время завершения работы приложения."""

    await aiohttp_session.session.close()  # type: ignore
    await orm_factory.db.stop()


async def main() -> None:

    """Функция, запускающая всё приложение."""

    await startup()
    await message_broker_factory.consume(
        queue_name=config.rabbit_mq.queue_raw_single_messages,
        callback=callback
    )
    await shutdown()


logging_config.dictConfig(LOGGING)
logger = logging.getLogger('email_formatter')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
