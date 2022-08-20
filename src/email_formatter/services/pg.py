from sqlalchemy import select, not_, and_

from db.models.email_single_notifications import SingleEmails
from db.models.email_templates import HTMLTemplates
from db.storage.abstract_classes import AbstractDBClient
from db.storage.orm_factory import db


class DBService:

    def __init__(self, database: AbstractDBClient):
        self.db = database

    async def get_raw_data_by_id(self, notification_id):
        query = select(
            SingleEmails.template_id,
            SingleEmails.destination_id,
            SingleEmails.message
        ).where(
            # and_(
                # SingleEmails.deleted_at is None,
                SingleEmails.id == notification_id
            # )
        )
        await self.db.start()
        return await self.db.execute(query)

    async def get_template_by_id(self, template_id):
        query = select(HTMLTemplates.template).where(HTMLTemplates.id == template_id)
        return await self.db.execute(query)

    async def put_passed_to_handled_at(self):
        ...


db_service = DBService(database=db)
