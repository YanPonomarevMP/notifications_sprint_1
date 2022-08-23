"""
Модуль содержит интерфейс для работы с сервисом форматирования email уведомлений.
В его обязанности входит получать данные о пользователе из разных мест и скрещивать их с шаблоном.
"""
from typing import Optional, Union
from uuid import UUID

from jinja2 import Environment
from pydantic import SecretStr

from email_formatter.models.all_data import AllData, AuthData
from email_formatter.services.auth import auth_service
from email_formatter.services.pg import db_service


class EmailFormatterService:

    """Класс с интерфейсом для Email Formatter Service."""

    async def get_data(
        self,
        notification_id: Union[UUID, str],
        x_request_id: str,
        authorization: SecretStr
    ) -> Optional[AllData]:
        """
        Метод достаёт данные.

        Args:
            notification_id: id сообщения
            x_request_id: id запроса
            authorization: access токен сервиса

        Returns:
            Вернёт pydantic модель AuthData, или None, если данное сообщение уже кем-то обрабатывается.
        """
        success = await db_service.mark_as_passed_to_handler(notification_id=notification_id)

        # Нам нужно обрабатывать сообщение, только если никто до нас его еще не взял его в обработку.
        # Метод db_service.mark_as_passed_to_handler решает сразу две задачи в одном запросе к БД:
        #
        # 1. Проставляет отметку, что мы приняли сообщение в обработку
        # 2. Если отметка уже стоит — скажет нам, что НЕ надо обрабатывать.
        if not success:  # Мы не смогли проставить отметку, а значит — кто-то другой уже взял.
            return None

        result = AllData()
        raw_data = await db_service.get_raw_data_by_id(notification_id=notification_id)

        if raw_data:  # А иначе (без этого условия) просто потеряем зря время, плюс лишние запросы.
            result.message = raw_data.message
            result.template = await db_service.get_template_by_id(template_id=raw_data.template_id)

            user_data = await auth_service.get_user_data_by_id(
                destination_id=raw_data.destination_id,
                x_request_id=x_request_id,
                authorization=authorization
            )
            result.user_data = AuthData(**user_data)

        return result

    async def render_html(self, template: str, data: dict) -> str:
        """
        Метод создаёт HTML на основе шаблона и данных.

        Args:
            template: шаблон
            data: данные для шаблона

        Returns:
            Вернёт сгенерированную строку HTML.
        """
        tmpl = Environment(enable_async=True).from_string(template)
        return await tmpl.render_async(**data)

    async def put_data(self):
        ...

    async def callback(self, message):
        ...

    async def start(self):
        ...


email_formatter_service = EmailFormatterService()
