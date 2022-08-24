"""Модуль содержит Pydantic модель для данных, приходящих из очереди."""
from typing import Union, Optional

from pydantic import validator

from email_formatter.models.base_config import BaseConfigModel


class DataFromQueue(BaseConfigModel):

    """Данные из очереди."""

    x_request_id: Union[str, dict]
    x_groups: Optional[Union[str, dict]]
    notification_id: Union[bytes, str]

    @validator('x_request_id')
    def x_request_id_to_str(cls, message: dict) -> str:
        """
        Метод выкусывает из словаря с заголовками нужный ключ.

        Args:
            message: сообщение

        Returns:
            Вернёт значение ключа.
        """
        return message['headers']['x-request-id']

    @validator('x_groups')
    def x_groups_to_str(cls, message: dict) -> Optional[str]:
        """
        Метод выкусывает из словаря с заголовками нужный ключ.

        Args:
            message: сообщение

        Returns:
            Вернёт значение ключа.
        """
        return message['headers'].get('x-group', None)

    @validator('notification_id')
    def byte_to_str(cls, message: bytes) -> str:
        """
        Метод декодирует содержимое сообщения (в данном случае notification_id).

        Args:
            message: сообщение

        Returns:
            Вернёт декодированную строку.
        """
        return message.decode()
