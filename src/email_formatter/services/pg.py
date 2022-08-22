from uuid import UUID

from pydantic import parse_obj_as
from sqlalchemy import select, and_

from db.models.email_single_notifications import SingleEmails
from db.models.email_templates import HTMLTemplates
from db.storage.abstract_classes import AbstractDBClient
from db.storage.orm_factory import db
from email_formatter.models.data_from_db import RawDataModel, TemplateModel


class DBService:

    def __init__(self, database: AbstractDBClient):
        self.db = database

    async def get_raw_data_by_id(self, notification_id: UUID) -> RawDataModel:
        query = self._get_query_select_raw_data(notification_id)

        async with self.db:
            result = await self.db.execute(query)

        # Результат можно, конечно, и в ручную перебрать, но выйдет громоздко.
        return parse_obj_as(RawDataModel, result[0]._mapping)

    async def get_template_by_id(self, template_id: UUID) -> TemplateModel:
        query = self._get_query_select_template_by_id(template_id)

        async with self.db:
            result = await self.db.execute(query)

        return parse_obj_as(TemplateModel, result[0]._mapping)  # TODO: А нужна ли тут модель вообще?

    async def put_passed_to_handled_at(self):
        ...

    def _get_query_select_raw_data(self, notification_id):
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

    def _get_query_select_template_by_id(self, template_id):
        return select(HTMLTemplates.template).filter(HTMLTemplates.id == template_id)


db_service = DBService(database=db)
