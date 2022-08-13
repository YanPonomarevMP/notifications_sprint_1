"""Модуль содержит всякие разные depends для FastAPI."""
import base64
import datetime
from enum import Enum
from typing import Callable, AsyncGenerator, Union

import aioredis
import orjson
from aioredis import Redis
from fastapi import Header, HTTPException, Depends, Request

# from api_config.settings import api_config
from notifier_api.models.event import EventValue, EventData, EventFromUser
from notifier_api.models.http_responses import http  # type: ignore
from notifier_api.models.tokens import AccessTokenData

from config.app_settings import config
from utils.aiohttp_session import get_session


async def authorization_required(
    authorization: str = Header(None),  # noqa: B008
    x_request_id: str = Header(None)  # noqa: B008
) -> None:
    """
    Функция не пропускает запросы без authorization.

    Args:
        authorization: access токен, который нужно проверить
        x_request_id: id запроса пользователя

    Raises:
        HTTPException:
            1. Если отсутствует Authorization вообще — ничего не спрашивая у Auth вываливаем исключение.

            2. Иначе, в случае, если Auth серверу не понравится наш токен —
            выплюнем его сообщение о том, что именно не так.
    """
    if not authorization:
        raise HTTPException(status_code=http.bad_request.code, detail=http.bad_request.message)

    session = await get_session()
    url = f'http://{config.auth_api.host}:{config.auth_api.port}{config.auth_api.url_check_token}'  # noqa: WPS237
    headers = {'X-Request-Id': x_request_id}
    json = {'access_token': authorization}

    response = await session.post(url, json=json, headers=headers)
    if response.status != http.ok.code:
        raise HTTPException(status_code=response.status, detail=await response.text())


async def parse_user_data_from_token(authorization: str = Header()) -> AccessTokenData:  # noqa: B008
    """
    Функция распарсивает токен.

    Args:
        authorization: access токен

    Returns:
        Вернёт Pydantic модель с пользовательскими данными.
    """
    payload_str = base64.b64decode(authorization.split('.')[1]).decode()
    payload = orjson.loads(payload_str)
    return AccessTokenData(**payload['sub'])


async def get_user_id_from_token(access_token: str) -> str:  # noqa: B008
    """
    Функция достаёт user_id из токена.

    Args:
        access_token: access токен

    Returns:
        Вернёт UUID пользователя.
    """
    payload = await parse_user_data_from_token(access_token)
    return payload.user_id


async def new_event(event: EventFromUser, user_id: str, topic: Union[str, Enum], method: str) -> EventData:
    """
    Функция создаёт модель с данными нового события.

    Args:
        event: данные о действии полученные от пользователя
        user_id: id пользователя
        topic: топик в котором надо зарегистрировать событие
        method: метод CRUD

    Returns:
        Возвращает модель pydantyc с данными события
    """
    event_value = EventValue(
        object_id=event.object_id,
        user_id=user_id,
        event_id=event.event_id,
        value=event.value,
        operation=method
    )

    return EventData(
        key=f'{event.object_id}_{user_id}',
        topic=topic,
        value=event_value
    )


async def x_request_id_required(x_request_id: str = Header(None)) -> None:  # noqa: B008
    """
    Функция не пропускает запросы без X-Request-Id.

    Args:
        x_request_id: ключ, который должен придти в заголовке запроса

    Raises:
        HTTPException: в случае отсутствия X-Request-Id

    """
    if not x_request_id:
        raise HTTPException(status_code=http.request_id_required.code, detail=http.request_id_required.message)


async def get_redis_connect() -> AsyncGenerator:
    """
    Функция создаёт соединение с базой данных на время работы функции, которая вызывает эту функцию через Depends.

    Подробнее см.
    https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/#a-database-dependency-with-yield

    Yields:
        Вернёт соединение с базой данных.
    """
    connect = await aioredis.from_url(f'redis://{config.redis.host}:{config.redis.port}', db=0)  # noqa: WPS237,WPS221
    try:  # noqa: WPS501
        yield connect

    finally:
        await connect.close()


def requests_per_minute(limiter: int) -> Callable:

    """
    Функция-замыкание.

    Она пробрасывает ограничение кол-ва запросов в минуту (limitter) в область видимости асинхронной функции inner.
    В свою очередь inner выполняет rate limiter. Именно эту корутину будем использовать в Depends.

    Args:
        limiter: ограничение кол-ва запросов в минуту

    Returns:
        Вернёт корутину, которую будут использовать ручки API в Depends (для ограничения к ним запросов).
    """

    async def inner(
        request: Request,
        redis_conn: Redis = Depends(get_redis_connect),  # noqa: B008
        authorization: str = Header(None)  # noqa: B008
    ) -> None:
        """
        Функция для ограничения числа запросов в минуту.

        Args:
            request: request запроса пользователя (из него нам нужен url path)
            redis_conn: соединение с Redis
            authorization: ключ в заголовке запроса (access токен пользователя)

        Raises:
            HTTPException:
                если кол-во запросов превысило лимит — гонит к чертям со словами извините, «Too Many Requests». :)
        """
        payload = await parse_user_data_from_token(authorization)
        user_id = payload.user_id

        now = datetime.datetime.now()
        key = f'{request.url.path}:{user_id}:{now.minute}'  # noqa: WPS237

        async with redis_conn.pipeline(transaction=True) as pipe:
            result_from_redis = await (
                pipe.incr(name=key, amount=1).expire(name=key, time=59).execute()  # type: ignore  # noqa: WPS432
            )

        request_number = result_from_redis[0]

        if request_number > limiter:
            raise HTTPException(status_code=http.too_many_requests.code, detail=http.too_many_requests.message)

    return inner
