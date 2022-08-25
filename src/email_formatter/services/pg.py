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
from email_formatter.models.log import log_names


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
        result = await self.db.execute(query)

        if result:
            row, = result
            logger.info(log_names.info.success_get, notification_id, 'single_emails table')
            return RawDataDB(**row._mapping)

        logger.error(log_names.error.failed_get, notification_id, 'single_emails table')
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
        result = await self.db.execute(query)

        if result:
            row, = result
            logger.info(log_names.info.success_get, template_id, 'html_templates table')
            return row.template

        logger.error(log_names.error.failed_get, template_id, 'html_templates table')
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
        result = await self.db.execute(query)

        if result is not None:  # Если None — метку не удалось поставить, а значит она уже стоит.
            logger.info(log_names.info.accepted, f'message with id {notification_id}')

        return bool(result)

    async def unmark_as_passed_to_handler(self, notification_id: Union[UUID, str]) -> None:
        query = self._get_query_unmark_as_passed_to_handler(notification_id)
        await self.db.execute(query)

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

    def _get_query_unmark_as_passed_to_handler(self, notification_id: Union[UUID, str]) -> Update:
        return update(
            SingleEmails
        ).filter(
            and_(
                SingleEmails.id == notification_id,
                SingleEmails.deleted_at == None
            )
        ).values(
            passed_to_handler_at=None
        )


logger = logging.getLogger('email_formatter.db_service')
db_service = DBService(database=db)
