"""Модуль содержит функцию для получения данных из RequestValidationError."""

from fastapi.exceptions import RequestValidationError

from notifier_api.models.access_log import RequestValidationErrorData


async def get_exception_data(exception: RequestValidationError) -> RequestValidationErrorData:
    """
    Функция парсит RequestValidationError.

    Args:
        exception: исключение RequestValidationError

    Returns:
        Вернёт pydantic модель c данными.
    """
    exc = RequestValidationErrorData()
    exc.detail = exception.errors()[0]  # type: ignore
    exc.source = exception.errors()[0]['loc'][0]  # type: ignore
    exc.field = exception.errors()[0]['loc'][1]  # type: ignore
    exc.msg = exception.errors()[0]['msg']  # type: ignore

    return exc
