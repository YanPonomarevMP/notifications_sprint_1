"""
Модуль содержит интерфейс для работы с сервисом форматирования email уведомлений.
В его обязанности входит получать данные о пользователе из разных мест и скрещивать их с шаблоном.
"""
from typing import Optional, Union
from uuid import UUID

from jinja2 import Environment

from email_formatter.models.all_data import AllData, AuthData
from email_formatter.services.auth import auth_service
from email_formatter.services.pg import db_service


class EmailFormatterService:

    """Класс с интерфейсом для Email Formatter Service."""

    async def get_data(self, notification_id: Union[UUID, str], x_request_id: str) -> Optional[AllData]:
        """
        Метод достаёт данные.

        Args:
            notification_id: id сообщения
            x_request_id: id запроса

        Returns:
            Вернёт pydantic модель AuthData.
        """
        result = AllData()
        raw_data = await db_service.get_raw_data_by_id(notification_id=notification_id)

        if raw_data:  # А иначе (без этого условия) просто потеряем зря время, плюс лишние запросы к БД и Auth, а зачем.
            result.message = raw_data.message  # type: ignore
            result.template = await db_service.get_template_by_id(template_id=raw_data.template_id)
            user_data = await auth_service.get_user_data_by_id(
                destination_id=raw_data.destination_id,
                x_request_id=x_request_id
            )
            result.user_data = AuthData(**user_data)  # type: ignore
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
        tmpl = Environment(enable_async=True, autoescape=True).from_string(template)
        return await tmpl.render_async(**data)

    def data_is_valid(self, data: Optional[AllData]) -> bool:
        """
        Метод проверяет валидность данных.
        Все ли данные на месте, или может что-то наш сервис найти не сумел?

        Args:
            data: данные, которые нужно проверить

        Returns:
            Вернёт ответ на вопрос все ли данные на месте, или может что-то наш сервис найти не сумел?
        """
        return all(data.dict()) and all(data.user_data.dict())  # type: ignore

    def groups_match(self, user_group: list, message_group: str) -> bool:
        """
        Метод сверяет группу сообщения с группами, в которых состоит пользователь.
        Если сообщение срочное —
        message_group будет равна None и в этом случае сообщение отправится,
        а иначе будем смотреть совпадает ли группа сообщения с одной из групп пользователя.

        Args:
            user_group: группы пользователя
            message_group: группа сообщения

        Returns:
            Вернёт ответ на вопрос можем ли посылать данное сообщение пользователю из исходя из групп.
        """
        if message_group is None:
            return True

        return message_group in user_group

    async def start_transaction(self, notification_id: Union[UUID, str]) -> bool:
        """
        Метод проставляет отметку в БД, что сообщение взято в обработку, тем самым имитируя начало транзакции.

        Args:
            notification_id: id сообщения

        Returns:
            Вернёт ответ на вопрос удалось ли проставить отметку.
            Если нет — значит кто-то до нас её уже проставил, а значит это сообщение уже не наше дело.
        """
        return await db_service.mark_as_passed_to_handler(notification_id=notification_id)

    async def abort_transaction(self, notification_id: Union[UUID, str]) -> None:
        """
        Метод убирает отметку в БД, что сообщение взято в обработку, тем самым имитируя прерывание транзакции.

        Args:
            notification_id: id сообщения
        """
        await db_service.unmark_as_passed_to_handler(notification_id=notification_id)


email_formatter_service = EmailFormatterService()
