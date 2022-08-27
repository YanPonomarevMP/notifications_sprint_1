# Flake8: noqa
# type: ignore
"""Модуль содержит базовый класс."""
from pydantic import BaseModel


class BaseConfigModel(BaseModel):

    """Базовый класс с настройками по умолчанию для всех моделей."""

    class Config:
        """
        Настройки pydantic.
        Подробнее см.
        https://pydantic-docs.helpmanual.io/usage/model_config/
        """
        validate_assignment = True
