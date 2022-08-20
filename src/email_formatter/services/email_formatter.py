# from email_formatter.services.auth import auth_service
from email_formatter.services.pg import db_service


class EmailFormatterService:

    async def get_data(self, notification_id):
        template_id, destination_id, message = await db_service.get_raw_data_by_id(notification_id=notification_id)
        template = await db_service.get_template_by_id(template_id=template_id)
        # email = await auth_service.get_email_by_id(email_id=destination_id)
        return message, template  # , email

    async def render_html(self):
        ...

    async def put_data(self):
        ...

    async def callback(self, message):
        ...

    async def start(self):
        ...


email_formatter_service = EmailFormatterService()
