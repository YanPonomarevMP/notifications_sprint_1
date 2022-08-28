"""Модуль содержит класс с интерфейсом для GroupHandler."""
import logging
from typing import Union, List
from uuid import UUID, uuid4

from group_handler.models.all_data import NotificationData, FinalData
from group_handler.models.data_single_emails import DataSingleEmails
from group_handler.services.auth import auth_service
from group_handler.services.pg import db_service


class GroupHandler:

    """Класс с интерфейсом для GroupHandler."""

    async def get_data(self, notification_id: Union[UUID, str], x_request_id: str) -> FinalData:
        """
        Метод достаёт данные.

        Args:
            notification_id: id группового сообщения.
            x_request_id: id запроса

        Returns:
            Вернёт пачку данных.
        """
        result = NotificationData()
        raw_data = await db_service.get_raw_data_by_id(notification_id=notification_id)

        if raw_data:
            for user in await auth_service.get_by_group(raw_data.destination_id, x_request_id):
                row_single_emails = DataSingleEmails(**raw_data.dict())
                row_single_emails.id = uuid4()
                row_single_emails.destination_id = user.user_id  # type: ignore
                row_single_emails.group_id = notification_id  # type: ignore

                if raw_data.send_with_gmt:  # В противном случае отправлять немедленно.
                    row_single_emails.delay = self._create_delay(hours=user.hours, minutes=user.minutes)  # type: ignore

                result.users.append(row_single_emails)
        return FinalData(**result.dict())

    async def lock(self, notification_id: Union[UUID, str]) -> bool:
        """
        Метод проставляет отметку в БД, что сообщение взято в обработку.

        Args:
            notification_id: id сообщения

        Returns:
            Вернёт ответ на вопрос удалось ли проставить отметку.
            Если нет — значит кто-то до нас её уже проставил, а значит это сообщение уже не наше дело.
        """
        return await db_service.mark_as_passed_to_handler(notification_id=notification_id)

    async def unlock(self, notification_id: Union[UUID, str]) -> None:
        """
        Метод убирает отметку в БД, что сообщение взято в обработку.

        Args:
            notification_id: id сообщения
        """
        await db_service.unmark_as_passed_to_handler(notification_id=notification_id)

    async def post_data(self, users: List[dict]) -> None:
        """
        Метод записывает данные в SingleEmail.

        Args:
            users: пачка данных для вставки
        """
        await db_service.insert_to_single_emails(users)

    def _create_delay(self, hours: int, minutes: int) -> int:
        """
        Метод высчитывает задержку исходя из timezone пользователя, приходящую из Auth.

        Args:
            hours: кол-во часов
            minutes: колв-о минут

        Returns:
            Вернёт задержку.
        """
        seconds_in_day = 24 * 60 * 60
        seconds_in_hours = abs(hours) * 60 * 60
        seconds_in_minutes = minutes * 60

        total_seconds = seconds_in_hours + seconds_in_minutes

        if hours > 0:
            return seconds_in_day - total_seconds
        return total_seconds


logger = logging.getLogger('group_handler')
group_handler_service = GroupHandler()
