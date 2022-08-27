"""Модуль содержит кастомные исключения и хэндлеры для их обработки."""
# from logging import getLogger
#
# from fastapi import Request
# from fastapi.exceptions import RequestValidationError
# from fastapi.responses import ORJSONResponse
# from starlette.exceptions import HTTPException as StarletteHTTPException

from notifier_api.models.http_responses import http  # type: ignore
# from utils.request_logging_data import get_logging_data
# from utils.validation_exception_data import get_exception_data

#
# async def validation_exception_handler(request: Request, exception: RequestValidationError) -> ORJSONResponse:
#     """
#     Обработчик исключения RequestValidationError с логированием запроса.
#
#     Args:
#         request: клиентский http запрос
#         exception: исключение с ошибкой валидации
#
#     Returns:
#         Возвращает http response с данными ошибки
#     """
#
#     log = await get_logging_data(request.scope['headers'])
#     err = await get_exception_data(exception)
#
#     logger = getLogger(log.logger_name)
#     logger.error(f'{err.msg}: {err.source}.{err.field} | {log.message}')  # noqa: WPS221
#
#     return ORJSONResponse(
#         {'detail': err.detail},
#         status_code=http.request_validation_error.code
#     )
#
#
# async def http_exception_handler(request: Request, exception: StarletteHTTPException) -> ORJSONResponse:
#     """
#     Обработчик исключения HTTPException с логированием запроса.
#     Назначается на HTTPException из Starlette, а не на аналогичный из FastAPI.
#     https://fastapi.tiangolo.com/tutorial/handling-errors/?h=er#fastapis-httpexception-vs-starlettes-httpexception
#
#     Args:
#         request: клиентский http запрос
#         exception: исключение с ошибкой HTTP
#
#     Returns:
#         Возвращает http response с данными ошибки
#     """
#
#     log = await get_logging_data(request.scope['headers'])
#
#     logger = getLogger(log.logger_name)
#     logger.error(f'{exception.detail} | {log.message} {exception.status_code}')
#
#     return ORJSONResponse(
#         {'detail': exception.detail},
#         status_code=exception.status_code
#     )


class DataBaseError(Exception):

    """Класс с собственным исключением для работы с кешом и бд."""

    def __init__(
            self,
            db_name: str,
            message: str,
            error_type: str,
            critical: bool = False
    ) -> None:

        """
        Конструктор.

        Args:
            db_name: название базы данных
            message: выводимое сообщение об ошибке
            error_type: само возникшее исключение
            critical: критична ли ошибка, можно ли продолжить программу игнорируя её
        """
        self.db_name = db_name
        self.message = message
        self.error_type = error_type
        self.critical = critical

        super().__init__()

    def __str__(self) -> str:
        """Формат вывода сообщения."""
        return f'{self.db_name} | {self.message} {self.error_type}'
