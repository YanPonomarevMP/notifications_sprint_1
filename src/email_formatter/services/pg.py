# TODO: Навести красоту на логгеры.
"""
Модуль содержит сервис для работы с Postgres.
Уже высокоуровневая бизнес логика.
"""
import logging
from typing import Optional, Union
from uuid import UUID

from sqlalchemy import select, and_, update, func
from sqlalchemy.sql import Select, Update

from db.models.email_single_notifications import SingleEmails
from db.models.email_templates import HTMLTemplates
from db.storage.abstract_classes import AbstractDBClient
from db.storage.orm_factory import db
from email_formatter.models.data_from_db import RawDataDB


class DBService:

    """Класс для высокоуровневой работы с PG."""

    def __init__(self, database: AbstractDBClient) -> None:
        """
        Конструктор.

        Args:
            database: интерфейс для низкоуровневой работы с БД.
        """
        self.db = database

    async def get_raw_data_by_id(self, notification_id: Union[UUID, str]) -> Optional[RawDataDB]:
        """
        Метод достаёт «сырые» данные по notification_id

        Args:
            notification_id: id сообщения

        Returns:
            Вернёт pydantic модель RawDataModel.
        """
        query = self._get_query_select_raw_data(notification_id)  # SQLAlchemy query очень громоздко выглядит.
        async with self.db:
            result = await self.db.execute(query)

        if result:
            row, = result
            logger.info('Received data from single_emails table with id %s', notification_id)
            return RawDataDB(**row._mapping)

        logger.error('Failed to get data from single_emails table with id %s', notification_id)
        return None

    async def get_template_by_id(self, template_id: Union[UUID, str]) -> Optional[str]:
        """
        Метод достаёт шаблон по template_id.

        Args:
            template_id: id шаблона

        Returns:
            Вернёт HTML строку-шаблон.
        """
        query = self._get_query_select_template_by_id(template_id)  # SQLAlchemy query очень громоздко выглядит.
        async with self.db:
            result = await self.db.execute(query)

        if result:
            row, = result
            logger.info('Received data from html_templates table with id %s', template_id)
            return row.template

        logger.error('Failed to get data from html_templates table with id %s', template_id)
        return None

    async def mark_as_passed_to_handler(self, notification_id: Union[UUID, str]) -> bool:
        """
        Метод проставляет отметку о том, что сообщение взято в обработку (дабы не допустить коллизий).

        И возвращает ответ на вопрос:
        была ли запись взята первый раз, или её уже кто-то начал обрабатывать перед нами.

        Args:
            notification_id: id сообщения

        Returns:
            Вернёт ответ на вопрос: была ли запись взята первый раз, или её уже кто-то начал обрабатывать перед нами.
        """
        query = self._get_query_mark_as_passed_to_handler(notification_id)  # SQLAlchemy query очень громоздко выглядит.
        async with self.db:
            result = await self.db.execute(query)

        if result is not None:
            logger.info('Started processing the message with id %s', notification_id)

        return bool(result)

    def _get_query_select_raw_data(self, notification_id: Union[UUID, str]) -> Select:
        """
        Метод формирует SQLAlchemy запрос Select.

        Args:
            notification_id: id сообщения

        Returns:
            Вернёт SQLAlchemy запрос.
        """
        return select(
            SingleEmails.template_id,
            SingleEmails.destination_id,
            SingleEmails.message,
        ).filter(
            and_(
                SingleEmails.deleted_at == None,
                SingleEmails.id == notification_id
            )
        )

    def _get_query_select_template_by_id(self, template_id: Union[UUID, str]) -> Select:
        """
        Метод формирует SQLAlchemy запрос Select.

        Args:
            template_id: id шаблона

        Returns:
            Вернёт SQLAlchemy запрос.
        """
        return select(HTMLTemplates.template).filter(HTMLTemplates.id == template_id)

    def _get_query_mark_as_passed_to_handler(self, notification_id: Union[UUID, str]) -> Update:
        """
        Метод формирует SQLAlchemy запрос Update.

        Args:
            notification_id: id сообщения

        Returns:
            Вернёт SQLAlchemy запрос.
        """
        return update(
            SingleEmails
        ).filter(
            and_(
                SingleEmails.id == notification_id,
                SingleEmails.passed_to_handler_at == None,
                SingleEmails.deleted_at == None
            )
        ).values(
            passed_to_handler_at=func.now()
        ).returning(
            SingleEmails.id
        )


logger = logging.getLogger(__name__)
db_service = DBService(database=db)
