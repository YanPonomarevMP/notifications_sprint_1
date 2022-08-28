"""Модуль содержит тесты."""
from typing import Callable

import pytest

from tests.functional.testdata.scenarios import scenarios


# Единый декоратор для всех асинхронных тестов (https://github.com/pytest-dev/pytest-asyncio#pytestmarkasyncio)
pytestmark = pytest.mark.asyncio


async def test_api_scenarios(make_get_request: Callable) -> None:
    """
    Функция тестирует API приложения по сценарию запросов
    Args:
        make_get_request: фикстура выполняющая HTTP запрос
    """

    # Выполнение запросов по сценарию
    for query in scenarios:
        response = await make_get_request(
            method=query.method,
            handle=query.url,
            headers=query.headers,
            params=query.params,
            body=query.body
        )
        assert response.status == query.expected_status
        if query.check_body:
            assert response.body == query.expected_body
        if query.check_len_body:
            assert len(response.body) == len(query.expected_body)
        if query.check_len_str_body:
            assert len(str(response.body)) == len(str(query.expected_body))

