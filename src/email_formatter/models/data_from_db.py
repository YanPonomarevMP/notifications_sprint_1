"""Модель содержит pydantic модели для RawData из DB."""
from typing import Union
from uuid import UUID

import orjson
from pydantic import validator

from email_formatter.models.base_config import BaseConfigModel  # type: ignore


class RawDataDB(BaseConfigModel):

    """Класс с «сырыми» данными из DB."""

    template_id: UUID
    destination_id: UUID
    message: Union[dict, str]
    group_id: UUID

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
