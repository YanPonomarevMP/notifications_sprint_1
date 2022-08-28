"""
Модуль содержит сервис для работы с Postgres.
Уже высокоуровневая бизнес логика.
"""
import logging
from typing import Union, Optional, List
from uuid import UUID

from sqlalchemy import and_, update, func, select, insert

from config.settings import config
from db.message_brokers.rabbit_message_broker import message_broker_factory
from db.models.email_group_notifications import GroupEmails
from db.models.email_single_notifications import SingleEmails
from db.storage.abstract_classes import AbstractDBClient
from db.storage.orm_factory import db
from group_handler.models.raw_data_db import RawDataDB


class DBService:  # noqa: WPS214

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
        Метод достаёт «сырые» данные по notification_id.

        Args:
            notification_id: id сообщения

        Returns:
            Вернёт pydantic модель RawDataModel.
        """
        query = select(
            GroupEmails.source,
            GroupEmails.destination_id,
            GroupEmails.template_id,
            GroupEmails.subject,
            GroupEmails.message,
            GroupEmails.send_with_gmt
        ).filter(
            and_(
                GroupEmails.deleted_at == None,  # noqa: E711
                GroupEmails.id == notification_id
            )
        )
        result = await self.db.execute(query)

        if result:
            row, = result
            # logger.info(log_names.info.success_get, notification_id, 'single_emails table')
            return RawDataDB(**row._mapping)  # noqa: WPS437

        # logger.error(log_names.error.failed_get, notification_id, 'single_emails table')
        return None


    async def mark_as_passed_to_handler(self, notification_id: Union[UUID, str]) -> bool:
        """
        Метод проставляет отметку о том, что сообщение взято в обработку (дабы не допустить коллизий).

        И возвращает ответ на вопрос:
        была ли запись взята первый раз, или её уже кто-то начал обрабатывать перед нами.

        PS:
        Возможно не совсем верно смешивать два действия в одном методе,
        однако, когда для меня стоял выбор, что сделать:

        1. два запроса к БД, но раздельные методы типа
        def mark_as_passed_to_handler() -> None
        def someone_already_took() -> bool

        2. Один запрос к БД, но, возможно, менее читаемо (реализовано сейчас)

        Я выбрала второй вариант, т.к. жертвовать запросами мне видится более критично.

        Args:
            notification_id: id сообщения

        Returns:
            Вернёт ответ на вопрос была ли запись взята первый раз, или её уже кто-то начал обрабатывать перед нами.
        """
        query = update(
            GroupEmails
        ).filter(
            and_(
                GroupEmails.id == notification_id,
                GroupEmails.passed_to_handler_at == None,  # noqa: E711
                GroupEmails.deleted_at == None  # noqa: E711
            )
        ).values(
            passed_to_handler_at=func.now()
        ).returning(
            GroupEmails.id
        )
        result = await self.db.execute(query)

        # if result is not None:  # Если None — метку не удалось поставить, а значит она уже стоит.
        # logger.info(log_names.info.accepted, f'message with id {notification_id}')

        return bool(result)

    async def unmark_as_passed_to_handler(self, notification_id: Union[UUID, str]) -> None:
        """
        Метод убирает отметку о том, что сообщение взято в обработку (дабы не допустить коллизий).

        Args:
            notification_id: id сообщения
        """
        query = update(
            GroupEmails
        ).filter(
            and_(
                GroupEmails.id == notification_id,
                GroupEmails.deleted_at == None  # noqa: E711
            )
        ).values(
            passed_to_handler_at=None
        )
        await self.db.execute(query)

    async def insert_to_single_emails(self, all_data: List[dict], x_request_id: str):
        query = insert(
            SingleEmails
        ).values(
            all_data
        )
        await self.db.execute(query)

        for row in all_data:
            await message_broker_factory.publish(
                message_body=str(row['id']).encode(),
                queue_name=config.rabbit_mq.queue_raw_single_messages,
                message_headers={'x-request-id': x_request_id},
                delay=row['delay']
            )


logger = logging.getLogger('group_handler.db_service')
db_service = DBService(database=db)
