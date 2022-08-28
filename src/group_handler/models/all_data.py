"""Модуль содержит pydantic классы."""
from typing import List, Optional
from uuid import UUID

from group_handler.models.base_config import BaseConfigModel
from group_handler.models.data_single_emails import DataSingleEmails


class AuthData(BaseConfigModel):

    """Данные из Auth."""

    user_id: Optional[UUID]
    hours: Optional[int]
    minutes: Optional[int]


class NotificationData(BaseConfigModel):

    """«Сырые» данные из сервиса."""

    users: List[DataSingleEmails] = []


class FinalData(BaseConfigModel):

    """Итоговые данные, что вернёт get_data."""

    users: List[DataSingleEmails]
