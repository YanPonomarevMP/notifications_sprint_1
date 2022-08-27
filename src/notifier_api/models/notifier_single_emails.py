"""Модуль содержит pydantic модели входящих данных ручки /single_emails."""
from datetime import datetime
from typing import Optional, Union, List, Dict
from uuid import UUID

from fastapi import HTTPException
from models.base_orjson import BaseOrjson  # type: ignore
from pydantic import validator, ValidationError

from notifier_api.models.http_responses import http  # type: ignore
from notifier_api.models.notifier_base_models import IdempotencyKeyChecker
from utils.validation_exception_data import parse_pydantic_validation_exception


class SingleEmailsRequest(BaseOrjson):

    """Данные, поступившие от клиента."""

    source: str
    destination_id: UUID
    template_id: UUID
    subject: str
    message: Dict
    delay: int


class SingleEmailsRequestUpdate(BaseOrjson):

    """Данные, поступившие от клиента."""

    id: UUID
    source: str
    destination_id: UUID
    template_id: UUID
    subject: str
    message: Dict
    delay: int


class SingleEmailsQuery(BaseOrjson):

    """Модель для работы с данными при обработке запроса"""

    id: Optional[UUID]
    source: Optional[str]
    destination_id: Optional[UUID]
    template_id: Optional[UUID]
    subject: Optional[str]
    message: Optional[Dict]
    delay: Optional[int]
    emails_selected: Optional[List[Dict]]
    msg: Optional[Union[datetime, str]]

    class Config:
        """Настройка валидации при изменении значения поля."""

        validate_assignment = True

    @validator('id', pre=True)
    def encode_to_bytes(cls, filed_value: UUID) -> UUID:  # noqa: WPS110, N805
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


class SingleEmailsResponse(BaseOrjson):

    """Формат ответа UGC API."""

    id: Optional[UUID]
    msg: Optional[Union[datetime, str]]


class SingleEmailsResponseSelected(BaseOrjson):

    """Формат ответа UGC API."""

    msg: Optional[str]
    emails_selected: Optional[List[Dict]]