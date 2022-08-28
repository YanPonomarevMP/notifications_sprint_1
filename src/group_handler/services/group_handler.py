import logging
from typing import Union
from uuid import UUID

from group_handler.models.all_data import NotificationData, FinalData
from group_handler.models.data_single_emails import DataSingleEmails
from group_handler.services.auth import auth_service
from group_handler.services.pg import db_service


class GroupHandler:

    async def get_data(self, notification_id: Union[UUID, str], x_request_id: str):
        result = NotificationData()
        raw_data = await db_service.get_raw_data_by_id(notification_id=notification_id)

        if raw_data:
            result.send_with_gmt = raw_data.send_with_gmt

            for user in await auth_service.get_by_group(raw_data.destination_id, x_request_id):
                row_single_emails = DataSingleEmails(**raw_data.dict())
                row_single_emails.destination_id = user.user_id
                row_single_emails.group_id = notification_id
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

    # async def unlock(self, notification_id: Union[UUID, str]) -> None:
    #     """
    #     Метод убирает отметку в БД, что сообщение взято в обработку.
    #
    #     Args:
    #         notification_id: id сообщения
    #     """
    #     await db_service.unmark_as_passed_to_handler(notification_id=notification_id)


logger = logging.getLogger('group_handler')
group_handler_service = GroupHandler()
