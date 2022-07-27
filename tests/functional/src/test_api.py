"""Модуль содержит тесты."""
from typing import Callable

import pytest

from tests.functional.settings import settings

# Единый декоратор для всех асинхронных тестов (https://github.com/pytest-dev/pytest-asyncio#pytestmarkasyncio)
pytestmark = pytest.mark.asyncio


async def test_api_events_post(
    make_request_post: Callable,
    authorization: str,
    x_request_id: str
) -> None:

    headers = {'X-Request-Id': x_request_id, 'Authorization': authorization}
    body = {"topic": "views", "key": "film1+user1", "value": "value_1"}
    handle = settings.ugc_api.handle_events_post

    # Пробуем выполнить корректный запрос.
    response = await make_request_post(handle=handle, headers=headers, body=body)
    assert response.status == 200

    # Пробуем выполнить запрос без Authorization (access токен)
    del headers['Authorization']
    response = await make_request_post(handle=handle, headers=headers, body=body)
    assert response.status == 400

    # Пробуем выполнить запрос без X-Request-Id.
    del headers['X-Request-Id']
    response = await make_request_post(handle=handle, headers=headers, body=body)
    assert response.status == 400
