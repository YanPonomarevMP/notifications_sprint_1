"""
Модуль содержит интерфейс для работы с сервисом отправки email уведомлений.
В его обязанности входит получать письмо и отправлять его в SMTP сервер.
"""
import logging
from email.message import EmailMessage
from typing import Union
from uuid import UUID

import aiosmtplib

from config.settings import config
from email_sender.models.message_data import MessageData
from email_sender.services.pg import db_service


class EmailSenderService:

    """Класс с интерфейсом email_sender."""

    def create_notification(self, message_data: MessageData) -> EmailMessage:
        """
        Метод создаёт сообщение для отправки в SMTP.

        Args:
            message_data: данные, из которых будем клепать сообщение.

        Returns:
            Вернёт EmailMessage объект.
        """
        notification = EmailMessage()
        notification['From'] = config.smtp.email_address
        notification['To'] = ','.join([message_data.to])  # type: ignore
        notification['Subject'] = message_data.subject
        notification['Reply-to'] = message_data.reply_to
        content = message_data.html
        notification.add_alternative(content, subtype='html')
        return notification

    async def post_notification(self, notification: EmailMessage) -> str:
        """
        Метод отправляет сообщение в SMTP.

        Args:
            notification: сообщение.

        Returns:
            Вернёт ответ сервера.
        """
        response = await aiosmtplib.send(
            notification,
            hostname=config.smtp.host,
            port=config.smtp.port,
            username=config.smtp.login.get_secret_value(),
            password=config.smtp.password.get_secret_value(),
            use_tls=True
        )
        return response[1]

    async def lock(self, notification_id: Union[UUID, str]) -> bool:
        """
        Метод проставляет отметку в БД, что сообщение взято в обработку.

        Args:
            notification_id: id сообщения

        Returns:
            Вернёт ответ на вопрос удалось ли проставить отметку.
            Если нет — значит кто-то до нас её уже проставил, а значит это сообщение уже не наше дело.
        """
        return await db_service.mark_as_sent_at(notification_id=notification_id)

    async def unlock(self, notification_id: Union[UUID, str]) -> None:
        """
        Метод убирает отметку в БД, что сообщение взято в обработку.

        Args:
            notification_id: id сообщения
        """
        await db_service.unmark_as_sent_at(notification_id=notification_id)

    async def post_response(self, notification_id: Union[UUID, str], response: str) -> None:
        """
        Метод записывает в БД ответ из SMTP сервера.

        Args:
            notification_id: id сообщения
            response: ответ сервера
        """
        await db_service.mark_as_sent_result(notification_id=notification_id, result=response)


logger = logging.getLogger('email_sender')
sender_service = EmailSenderService()
