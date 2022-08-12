"""Модуль содержит сессию aiohttp."""
from typing import Optional

from aiohttp import ClientSession

session: Optional[ClientSession] = None


async def get_session() -> ClientSession:
    """Функция возвращает storage."""
    return session  # type: ignore
