"""Модуль содержит pydantic модели."""
from typing import Optional, List

from email_formatter.models.base_config import BaseConfigModel


class AuthData(BaseConfigModel):

    """Все данные о пользователе, приходящие из Auth."""

    name: Optional[str]
    email: Optional[str]
    groups: Optional[List[str]]


class AllData(BaseConfigModel):

    """Все данные, которые сервис юзает."""

    user_data: Optional[AuthData]
    template: Optional[str]
    message: Optional[dict]
