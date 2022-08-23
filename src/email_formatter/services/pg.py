import logging
from typing import Optional, Union
from uuid import UUID

from sqlalchemy import select, and_, update, func
from sqlalchemy.sql import Select, Update

from db.models.email_single_notifications import SingleEmails
from db.models.email_templates import HTMLTemplates
from db.storage.abstract_classes import AbstractDBClient
from db.storage.orm_factory import db
from email_formatter.models.data_from_db import RawDataModel


class DBService:

    def __init__(self, database: AbstractDBClient) -> None:
        self.db = database

    async def get_raw_data_by_id(self, notification_id: Union[UUID, str]) -> Optional[RawDataModel]:
        query = self._get_query_select_raw_data(notification_id)
        async with self.db:
            result = await self.db.execute(query)

        if result:
            row, = result
            return RawDataModel(**row._mapping)

        logger.error('Failed to get data from single_emails table with id %s', notification_id)
        return None

    async def get_template_by_id(self, template_id: Union[UUID, str]) -> Optional[str]:
        query = self._get_query_select_template_by_id(template_id)
        async with self.db:
            result = await self.db.execute(query)

        if result:
            return result.template

        logger.error('Failed to get data from html_templates table with id %s', template_id)
        return None

    async def mark_as_passed_to_handler(self, notification_id: Union[UUID, str]) -> None:
        query = self._get_query_mark_as_passed_to_handler(notification_id)
        async with self.db:
            await self.db.execute(query)

        logger.info('Started processing the message with id %s', notification_id)

    def _get_query_select_raw_data(self, notification_id: Union[UUID, str]) -> Select:
        return select(
            SingleEmails.template_id,
            SingleEmails.destination_id,
            SingleEmails.message,
        ).filter(
            and_(
                SingleEmails.deleted_at == None,
                SingleEmails.passed_to_handler_at == None,
                SingleEmails.id == notification_id
            )
        )

    def _get_query_select_template_by_id(self, template_id: Union[UUID, str]) -> Select:
        return select(HTMLTemplates.template).filter(HTMLTemplates.id == template_id)

    def _get_query_mark_as_passed_to_handler(self, notification_id: Union[UUID, str]) -> Update:
        return update(
            SingleEmails
        ).filter(
            SingleEmails.id == notification_id
        ).values(
            passed_to_handler_at=func.now()
        )


logger = logging.getLogger(__name__)
db_service = DBService(database=db)
