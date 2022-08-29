"""Модуль содержит абстрактнее классы."""
from abc import ABC
from email.message import EmailMessage
from typing import Union
from uuid import UUID

from group_handler.models.message_data import MessageData


class AbstractSenderService(ABC):

    """Абстрактный класс с интерфейсом Sender Service."""

    def create_notification(self, message_data: MessageData) -> EmailMessage:
        """
        Метод создаёт сообщение для отправки в SMTP.

        Args:
            message_data: данные, из которых будем клепать сообщение.

        Returns:
            Вернёт EmailMessage объект.
        """
        pass

    async def post_notification(self, notification: EmailMessage) -> str:
        """
        Метод отправляет сообщение в SMTP.

        Args:
            notification: сообщение.

        Returns:
            Вернёт ответ сервера.
        """
        pass

    async def lock(self, notification_id: Union[UUID, str]) -> bool:
        """
        Метод проставляет отметку в БД, что сообщение взято в обработку.

        Args:
            notification_id: id сообщения

        Returns:
            Вернёт ответ на вопрос удалось ли проставить отметку.
            Если нет — значит кто-то до нас её уже проставил, а значит это сообщение уже не наше дело.
        """
        pass

    async def unlock(self, notification_id: Union[UUID, str]) -> None:
        """
        Метод убирает отметку в БД, что сообщение взято в обработку.

        Args:
            notification_id: id сообщения
        """
        pass

    async def post_response(self, notification_id: Union[UUID, str], response: str) -> None:
        """
        Метод записывает в БД ответ из SMTP сервера.

        Args:
            notification_id: id сообщения
            response: ответ сервера
        """
        pass
