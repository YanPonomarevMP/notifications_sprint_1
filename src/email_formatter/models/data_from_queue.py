"""Модуль содержит Pydantic модель для данных, приходящих из очереди."""
from typing import Union, Optional

from pydantic import validator

from email_formatter.models.base_config import BaseConfigModel  # type: ignore


class MessageData(BaseConfigModel):

    """Данные из очереди."""

    x_request_id: Union[str, dict]
    notification_id: Union[bytes, str]
    count_retry: Union[int, dict]

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

    @validator('count_retry')
    def dict_to_int(cls, message: dict) -> int:
        """
        Метод выкусывает из словаря с заголовками нужный ключ.

        Args:
            message: сообщение

        Returns:
            Вернёт count retry значение.
        """
        return message['headers']['x-death'][0]['count']
