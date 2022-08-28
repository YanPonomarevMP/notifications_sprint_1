"""Модуль содержит фикстуры для pytest."""
import asyncio
from typing import Optional, Callable, Generator

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
async def session() -> Generator:
    """Фикстура возвращает AIOHTTP сессию."""
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(session: aiohttp.ClientSession) -> Callable:
    """
    Фикстура возвращает функцию для выполнения запросов к API.
    Args:
        session: AIOHTTP сессия

    Returns:
        Возвращает функцию для выполнения запросов к API.
    """

    async def inner(
        method: str,
        handle: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        body: Optional[dict] = None
    ) -> HTTPResponse:
        """
        Функция выполняет http запрос.
        Args:
            handle: ручка API
            params: параметры запроса

        Returns:
            Pydantic модель с ответом сервера.
        """
        params = params or {}
        headers = headers or {}
        json = body or {}
        url = f'{settings.notifier_test_api.url}{settings.notifier_test_api.prefix}{handle}'

        async with session.post(url, json=json, headers=headers, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner
