"""Модель содержит pydantic модели для RawData из DB."""
from typing import Union
from uuid import UUID

import orjson
from pydantic import validator

from email_formatter.models.base_orjson import BaseOrjson


class RawDataModel(BaseOrjson):

    """Класс с «сырыми» данными из PG."""

    template_id: UUID
    destination_id: UUID
    message: Union[dict, str]

    @validator('message')
    def json_to_dict(cls, message: str) -> dict:
        """
        Метод преобразует JSON в dict.

        Args:
            message: JSON с данными

        Returns:
            Вернёт словарь.
        """
        return orjson.loads(message)


class TemplateModel(BaseOrjson):

    template: str
