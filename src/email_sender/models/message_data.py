"""Модуль содержит Pydantic модель для данных, приходящих из очереди."""
from typing import Union

import orjson
from pydantic import validator

from email_sender.models.base_config import BaseConfigModel


class MessageData(BaseConfigModel):

    """Данные из очереди."""

    x_request_id: Union[str, dict]
    count_retry: Union[int, dict]
    notification_id: Union[str, bytes]
    html: Union[str, bytes]
    from_user: Union[str, bytes]
    to_user: Union[str, bytes]
    subject: Union[str, bytes]

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

    @validator('notification_id')
    def get_notification_id(cls, message: bytes) -> str:
        return orjson.loads(message)['notification_id']

    @validator('html')
    def get_html(cls, message: bytes) -> str:
        return orjson.loads(message)['html']

    @validator('from_user')
    def get_from_user(cls, message: bytes) -> str:
        return orjson.loads(message)['from']

    @validator('to_user')
    def get_to_user(cls, message: bytes) -> str:
        return orjson.loads(message)['to']

    @validator('subject')
    def get_subject(cls, message: bytes) -> str:
        return orjson.loads(message)['subject']
