from typing import Dict, Optional, Union
from uuid import UUID

import orjson
from pydantic import validator

from notifier_api.models.base_orjson import BaseOrjson


class MessageBrokerData(BaseOrjson):

    """Данные для загрузки в брокер сообщений."""

    message_body: Union[bytes, str, UUID, dict]
    queue_name: str
    message_headers: Optional[Dict]
    delay: Union[int, float] = 0

    class Config:

        """Настройка валидации при изменении значения поля."""

        validate_assignment = True

    @validator('message_body', pre=True)
    def encode_to_bytes(cls, filed_value: Union[str, UUID, dict]) -> bytes:  # noqa: WPS110, N805
        """
        Метод преобразует значение поля в байты.

        Args:
            filed_value: значение, которое нужно преобразовать в байты

        Returns:
            Вернёт байт строку.
        """
        return orjson.dumps(filed_value)