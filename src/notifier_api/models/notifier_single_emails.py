"""Модуль содержит pydantic модели входящих данных ручки /single_emails."""
from datetime import datetime
from typing import Optional, Union, List, Dict
from uuid import UUID

from models.base_orjson import BaseOrjson  # type: ignore

from notifier_api.models.http_responses import http  # type: ignore


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


class SingleEmailsResponse(BaseOrjson):

    """Формат ответа UGC API."""

    id: Optional[UUID]
    msg: Optional[Union[datetime, str]]


class SingleEmailsResponseSelected(BaseOrjson):

    """Формат ответа UGC API."""

    msg: Optional[str]
    emails_selected: Optional[List[Dict]]
