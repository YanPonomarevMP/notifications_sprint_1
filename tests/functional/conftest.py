"""Модуль содержит фикстуры для pytest."""
import asyncio
from typing import Generator, Callable, AsyncGenerator
from uuid import uuid4

import aiohttp
import pytest

from tests.functional.settings import settings
from tests.functional.testdata.models import HTTPResponse


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Фикстура подменяет цикл событий по умолчанию.
    Без этого тесты падают с ошибкой <Event loop is closed>.
    """
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def x_request_id() -> str:
    """Фикстура возвращает идентификатор запроса."""
    return str(uuid4)


@pytest.fixture(scope='session')
async def authorization() -> str:
    """Фикстура возвращает access токен."""
    return 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY1MzY1ODEzOSwianRpIjoiYTJiM2UwNGMtZWYzMC00NThjLTlmOTktOGZjNTNjZmRmNmQ0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpYXQiOiJGcmksIDI3IE1heSAyMDIyIDEzOjI4OjU5IEdNVCIsInR0bCI6MzAwMDAsInVzZXJfaWQiOiJlZmMzMTIzNy1hNWJmLTQxNGUtYmE5NS1mMTVmMGYxNmQzZjUiLCJ1c2VyX3JvbGVzIjpbXSwidXNlcl9maW5nZXJwcmludCI6IlBvc3RtYW5SdW50aW1lLzcuMjguNCIsImFjY2Vzc190b2tlbl9pZCI6IjdmNzI0ODc0LWQwMzgtNGEwOS1hMzA5LWUzOWFiMDZkZTg5OSIsInJlZnJlc2hfdG9rZW5faWQiOiJlODMzYTNkMi0xYzAzLTQ3YTAtYmRkOC0wYTRmMTE4ZjZkNDMifSwibmJmIjoxNjUzNjU4MTM5LCJleHAiOjE2NTM2ODgxMzl9.Ir8BbkPyGPByuDBzEqrpJZ99z3AcCICbyJWDgyESus4'


@pytest.fixture(scope='session')
async def session() -> AsyncGenerator:
    """Фикстура возвращает AIOHTTP сессию."""
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope='session')
def make_request_post(session: aiohttp.ClientSession) -> Callable:
    """
    Фикстура возвращает функцию для выполнения POST запросов к API.

    Args:
        session: AIOHTTP сессия

    Returns:
        Возвращает функцию для выполнения POST запросов к API.
    """

    async def inner(handle: str, headers: dict, body: dict) -> HTTPResponse:
        """Функция выполняет http запрос."""
        url = f'{settings.ugc_api.url}{settings.ugc_api.prefix}{handle}'

        async with session.post(url, json=body, headers=headers) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner
