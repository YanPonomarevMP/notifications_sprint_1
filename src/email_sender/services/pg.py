"""
Модуль содержит сервис для работы с Postgres.
Уже высокоуровневая бизнес логика.
"""
import logging
from typing import Union
from uuid import UUID

from sqlalchemy import and_, update, func

from db.models.email_single_notifications import SingleEmails
from db.storage.abstract_classes import AbstractDBClient
from db.storage.orm_factory import db
from email_sender.models.log import log_names


class DBService:  # noqa: WPS214

    """Класс для высокоуровневой работы с PG."""

    def __init__(self, database: AbstractDBClient) -> None:
        """
        Конструктор.

        Args:
            database: интерфейс для низкоуровневой работы с БД.
        """
        self.db = database

    async def mark_as_sent_at(self, notification_id: Union[UUID, str]) -> bool:
        """
        Метод ставит отметку о том, что сообщение отправлено.

        Args:
            notification_id: id сообщения
        """
        query = update(
            SingleEmails
        ).filter(
            and_(
                SingleEmails.id == notification_id,
                SingleEmails.sent_at == None,  # noqa: E711
                SingleEmails.deleted_at == None  # noqa: E711
            )
        ).values(
            sent_at=func.now()
        ).returning(
            SingleEmails.id
        )
        result = await self.db.execute(query)

        if result is not None:  # Если None — метку не удалось поставить, а значит она уже стоит.
            logger.info(log_names.info.accepted, f'message with id {notification_id}')

        return bool(result)

    async def unmark_as_sent_at(self, notification_id: Union[UUID, str]) -> None:
        """
        Метод убирает отметку о том, что сообщение отправлено.

        Args:
            notification_id: id сообщения
        """
        query = update(
            SingleEmails
        ).filter(
            and_(
                SingleEmails.id == notification_id,
                SingleEmails.deleted_at == None  # noqa: E711
            )
        ).values(
            sent_at=None
        )
        await self.db.execute(query)

    async def mark_as_sent_result(self, notification_id: Union[UUID, str], result: str) -> None:
        """
        Метод проставляет в БД ответ от SMTP сервера.

        Args:
            notification_id: id сообщения
            result: ответ сервера
        """
        query = update(
            SingleEmails
        ).filter(
            and_(
                SingleEmails.id == notification_id,
                SingleEmails.deleted_at == None  # noqa: E711
            )
        ).values(
            sent_result=result
        )
        await self.db.execute(query)


logger = logging.getLogger('email_sender.db_service')
db_service = DBService(database=db)
