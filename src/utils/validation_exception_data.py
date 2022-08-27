"""Модуль содержит функцию для получения данных из RequestValidationError."""

from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from notifier_api.models.access_log import RequestValidationErrorData, PydanticValidationErrorData


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


def parse_pydantic_validation_exception(exception: ValidationError) -> PydanticValidationErrorData:
    """
    Функция парсит ValidationError pydantic.

    Args:
        exception: исключение ValidationError

    Returns:
        Вернёт pydantic модель c данными.
    """
    exc = PydanticValidationErrorData()
    exc.detail = exception.errors()[0]  # type: ignore
    exc.source = exception.errors()[0]['loc'][0]  # type: ignore
    exc.msg = exception.errors()[0]['msg']  # type: ignore

    return exc
