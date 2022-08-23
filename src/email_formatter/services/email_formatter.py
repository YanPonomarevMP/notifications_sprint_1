import logging
from typing import Optional, Union
from uuid import UUID

from email_formatter.models.all_data import AllData
from email_formatter.services.auth import auth_service
from email_formatter.services.pg import db_service


class EmailFormatterService:

    async def get_data(
        self,
        notification_id: Union[UUID, str],
        x_request_id: str
    ) -> AllData:
        # await db_service.mark_as_passed_to_handler(notification_id=notification_id)

        result = AllData()
        raw_data = await db_service.get_raw_data_by_id(notification_id=notification_id)

        if raw_data:
            result.message = raw_data.message
            template = await db_service.get_template_by_id(template_id=raw_data.template_id)

            if template:
                result.template = template
                email = await auth_service.get_email_by_id(email_id=raw_data.destination_id, x_request_id=x_request_id)
                result.email = email

        return result

    async def render_html(self):
        ...

    async def put_data(self):
        ...

    async def callback(self, message):
        ...

    async def start(self):
        ...


email_formatter_service = EmailFormatterService()
