"""Модуль содержит pydantic модели входящих данных ручки /single_emails."""
from datetime import datetime
from typing import Optional, Union, List, Dict
from uuid import UUID

from models.base_orjson import BaseOrjson  # type: ignore

from notifier_api.models.notifier_single_emails import SingleEmailsRequest, SingleEmailsRequestUpdate, \
    SingleEmailsQuery, SingleEmailsSelected


class GroupEmailsRequest(SingleEmailsRequest):

    """Данные, поступившие от клиента."""

    send_with_gmt: bool


class GroupEmailsRequestUpdate(SingleEmailsRequestUpdate):

    """Данные, поступившие от клиента."""

    send_with_gmt: bool


class GroupEmailsQuery(SingleEmailsQuery):

    """Модель для работы с данными при обработке запроса."""

    send_with_gmt: Optional[bool]

    class Config:
        """Настройка валидации при изменении значения поля."""

        validate_assignment = True


class GroupEmailsResponse(BaseOrjson):

    """Формат ответа UGC API."""

    id: Optional[UUID]
    msg: Optional[Union[datetime, str]]


class GroupEmailsSelected(SingleEmailsSelected):

    """Данные, поступившие от клиента."""

    send_with_gmt: Optional[bool]


class GroupEmailsResponseSelected(BaseOrjson):

    """Формат ответа UGC API."""

    msg: Optional[str]
    emails_selected: Optional[List[Dict]]
