"""
Модуль содержит интерфейс для работы с сервисом форматирования email уведомлений.
В его обязанности входит получать данные о пользователе из разных мест и скрещивать их с шаблоном.
"""
from typing import Optional, Union
from uuid import UUID

from jinja2 import Environment
from pydantic import SecretStr

from db.message_brokers.rabbit_message_broker import message_broker_factory
from email_formatter.models.all_data import AllData, AuthData
from email_formatter.services.auth import auth_service
from email_formatter.services.pg import db_service


class EmailFormatterService:

    """Класс с интерфейсом для Email Formatter Service."""

    async def get_data(self, notification_id: Union[UUID, str]) -> Optional[AllData]:
        """
        Метод достаёт данные.

        Args:
            notification_id: id сообщения

        Returns:
            Вернёт pydantic модель AuthData, или None, если данное сообщение уже кем-то обрабатывается.
        """
        success = await db_service.mark_as_passed_to_handler(notification_id=notification_id)

        # Нам нужно обрабатывать сообщение, только если никто до нас еще не взял его в обработку.
        # Метод db_service.mark_as_passed_to_handler решает сразу две задачи в одном запросе к БД:
        #
        # 1. Проставляет отметку, что мы приняли сообщение в обработку
        # 2. Если отметка уже стоит — скажет нам, что НЕ надо обрабатывать.
        if not success:
            return None  # Мы не смогли проставить отметку, а значит — кто-то другой уже проставил её до нас.

        result = AllData()
        raw_data = await db_service.get_raw_data_by_id(notification_id=notification_id)

        if raw_data:  # А иначе (без этого условия) просто потеряем зря время, плюс лишние запросы к БД и Auth, а зачем.
            result.message = raw_data.message
            result.template = await db_service.get_template_by_id(template_id=raw_data.template_id)

            user_data = await auth_service.get_user_data_by_id(destination_id=raw_data.destination_id)
            result.user_data = AuthData(**user_data)

        return result

    async def render_html(self, template: str, data: dict) -> bytes:
        """
        Метод создаёт HTML на основе шаблона и данных.

        Args:
            template: шаблон
            data: данные для шаблона

        Returns:
            Вернёт сгенерированную строку HTML.
        """
        tmpl = Environment(enable_async=True).from_string(template)
        result = await tmpl.render_async(**data)
        return result.encode()

    async def put_data(
        self,
        message_body: bytes,
        queue_name: str,
        message_headers: dict
    ):
        await message_broker_factory.publish(
            message_body=message_body,
            queue_name=queue_name,
            message_headers=message_headers
        )

    def data_is_valid(self, data: Optional[AllData]) -> bool:
        """
        Метод проверяет валидность данных.
        Все ли данные на месте, или может что-то наш сервис найти не сумел?

        Args:
            data: данные, которые нужно проверить

        Returns:
            Вернёт ответ на вопрос: Все ли данные на месте, или может что-то наш сервис найти не сумел?
        """
        if data is None:
            return False
        return all(data.dict()) and all(data.user_data.dict())

    def can_send(self, user_group: list, message_group: str) -> bool:
        """
        Метод сверяет группу сообщения с группами, в которых состоит пользователь.
        Если сообщение срочное —
        message_group будет равна None и в этом случае сообщение отправится,
        а иначе будем смотреть совпадает ли группа сообщения с одной из групп пользователя.

        Args:
            user_group:
            message_group:

        Returns:
            Вернёт ответ на вопрос можем ли м посылать данное сообщение пользователю из исходя из групп.
        """
        if message_group is None:
            return True

        return message_group in user_group


email_formatter_service = EmailFormatterService()
