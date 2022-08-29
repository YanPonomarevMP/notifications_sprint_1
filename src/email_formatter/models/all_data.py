"""Модуль содержит pydantic модели."""
from typing import Optional, List
from uuid import UUID

from email_formatter.models.base_config import BaseConfigModel  # type: ignore


class AuthData(BaseConfigModel):

    """Все данные о пользователе, приходящие из Auth."""

    name: Optional[str]
    email: Optional[str]
    groups: Optional[list[UUID]]


class NotificationData(BaseConfigModel):

    """Все данные, которые сервис юзает."""

    user_data: Optional[AuthData]
    template: Optional[str]
    message: Optional[dict]
    group: Optional[UUID]
    source: Optional[str]
    subject: Optional[str]


class FinalAuth(BaseConfigModel):

    """Все данные о пользователе, приходящие из Auth."""

    name: str
    email: str
    groups: List[UUID]


class FinalData(BaseConfigModel):

    """Все данные, которые сервис юзает."""

    user_data: FinalAuth
    template: str
    message: dict
    group: Optional[UUID]
    source: str
    subject: str
