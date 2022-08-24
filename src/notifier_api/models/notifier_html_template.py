"""Модель содержит pydantic модели входящих данных ручки /html_templates."""
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from models.base_orjson import BaseOrjson  # type: ignore
from pydantic import validator, ValidationError

from notifier_api.models.http_responses import http  # type: ignore
from utils.validation_exception_data import parse_pydantic_validation_exception


class IdempotencyKeyChecker(BaseOrjson):

    """
    Модель для проверки корректности UUID.
    В случае ошибки она вызовет ValidationError,
    которое будет перехвачено валидатором основной модели
    """

    idempotency_key: Optional[UUID]


class HtmlTemplate(BaseOrjson):

    """Данные, поступившие от клиента."""

    id: Optional[UUID]
    title: str
    template: str

    class Config:
        """Настройка валидации при изменении значения поля."""

        validate_assignment = True

    @validator('id', pre=True)
    def encode_to_bytes(cls, filed_value: str) -> UUID:  # noqa: WPS110, N805
        """
        Метод проверяет корректность UUID и вызывает HTTPException вместо ValidationError.
        Это позволяет отправить клиенту 400 вместо 500 и записать ошибку в лог.

        Args:
            filed_value: значение, которое нужно проверить

        Returns:
            Вернёт UUID.

        Raises:
            HTTPException:
                В случае некорректного ID вызовет HTTPException.
        """
        try:
            good_uuid = IdempotencyKeyChecker(idempotency_key=filed_value)

        except ValidationError as exception:
            err = parse_pydantic_validation_exception(exception)

            raise HTTPException(
                status_code=http.request_validation_error.code,
                detail=f'{err.msg} - {err.source}'
            )
        return good_uuid.idempotency_key
