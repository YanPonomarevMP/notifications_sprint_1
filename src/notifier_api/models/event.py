"""Модель содержит pydantic модели для event."""
from enum import Enum
from typing import Optional, Union

from pydantic import validator

from models.base_orjson import BaseOrjson  # type: ignore


class EventFromUser(BaseOrjson):

    """Данные, поступившие от клиента."""

    object_id: str
    event_id: str
    value: str


class EventValue(BaseOrjson):

    """Данные о событии для записи в БД."""

    object_id: str
    user_id: Optional[str]
    event_id: str
    value: str
    operation: str


class EventData(BaseOrjson):

    """Данные, для вставки в БД."""

    topic: Optional[Union[str, Enum]]
    key: Optional[str]
    value: EventValue  # noqa: WPS110

    class Config:

        """Настройка валидации при изменении значения поля."""

        validate_assignment = True

    @validator('key')
    def encode_to_bytes(cls, filed_value: str) -> bytes:  # noqa: WPS110, N805
        """
        Метод преобразует key в байты.

        Подробнее см.
        https://pydantic-docs.helpmanual.io/usage/validators/

        Args:
            filed_value: значение, которое нужно преобразовать в байты

        Returns:
            Вернёт байт строку.
        """
        return filed_value.encode()
