"""Модуль содержит функции, запускаемые при старте и остановке FastAPI."""
import aiohttp

from config.settings import config
from db.message_brokers.rabbit_message_broker import message_broker_factory
from db.storage import orm_factory
from utils import aiohttp_session


async def startup() -> None:

    """Функция, для действий во время старта приложения."""

    headers = {'Authorization': config.auth_api.access_token.get_secret_value()}
    aiohttp_session.session = aiohttp.ClientSession(headers=headers)
    await message_broker_factory.idempotency_startup()

    # await event_broker.start()
    await orm_factory.db.start()


async def shutdown() -> None:

    """Функция, для действий во время завершения работы приложения."""

    await aiohttp_session.session.close()  # type: ignore
    # await event_broker.stop()
    await orm_factory.db.stop()
