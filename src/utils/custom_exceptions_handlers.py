"""Модуль содержит кастомные хэндлеры для обработки исключений."""
from logging import getLogger

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from notifier_api.models.http_responses import http  # type: ignore
from utils.request_logging_data import get_logging_data
from utils.validation_exception_data import get_exception_data


async def validation_exception_handler(request: Request, exception: RequestValidationError) -> ORJSONResponse:
    """
    Обработчик исключения RequestValidationError с логированием запроса.

    Args:
        request: клиентский http запрос
        exception: исключение с ошибкой валидации

    Returns:
        Возвращает http response с данными ошибки
    """

    log = await get_logging_data(request.scope['headers'])
    err = await get_exception_data(exception)

    logger = getLogger(log.logger_name)
    logger.error(f'{err.msg}: {err.source}.{err.field} | {log.message}')  # noqa: WPS221

    return ORJSONResponse(
        {'detail': err.detail},
        status_code=http.request_validation_error.code
    )


async def http_exception_handler(request: Request, exception: StarletteHTTPException) -> ORJSONResponse:
    """
    Обработчик исключения HTTPException с логированием запроса.
    Назначается на HTTPException из Starlette, а не на аналогичный из FastAPI.
    https://fastapi.tiangolo.com/tutorial/handling-errors/?h=er#fastapis-httpexception-vs-starlettes-httpexception

    Args:
        request: клиентский http запрос
        exception: исключение с ошибкой HTTP

    Returns:
        Возвращает http response с данными ошибки
    """

    log = await get_logging_data(request.scope['headers'])

    logger = getLogger(log.logger_name)
    logger.error(f'{exception.detail} | {log.message} {exception.status_code}')

    return ORJSONResponse(
        {'detail': exception.detail},
        status_code=exception.status_code
    )
