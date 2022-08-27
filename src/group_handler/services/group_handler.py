import logging
from typing import Optional, Union
from uuid import UUID

from group_handler.services.pg import db_service


class GroupHandler:

    # async def get_data(self, notification_id: Union[UUID, str], x_request_id: str) -> Optional[FinalData]:
    #     """
    #     Метод достаёт данные.
    #
    #     Args:
    #         notification_id: id сообщения
    #         x_request_id: id запроса
    #
    #     Returns:
    #         Вернёт pydantic модель AuthData.
    #     """
    #     result = NotificationData()
    #     raw_data = await db_service.get_raw_data_by_id(notification_id=notification_id)
    #
    #     if raw_data:
    #         result.message = raw_data.message  # type: ignore
    #         result.group = raw_data.group_id
    #         result.subject = raw_data.subject
    #         result.source = raw_data.source
    #         result.template = await db_service.get_template_by_id(template_id=raw_data.template_id)
    #         user_data = await auth_service.get_user_data_by_id(
    #             destination_id=raw_data.destination_id,
    #             x_request_id=x_request_id
    #         )
    #         result.user_data = AuthData(**user_data)  # type: ignore
    #     result.message.update(result.user_data)  # type: ignore
    #     return FinalData(**result.dict())
    #
    # def check_subscription(self, user_group: list, message_group: str) -> bool:
    #     """
    #     Метод сверяет группу сообщения с группами, в которых состоит пользователь.
    #     Если сообщение срочное —
    #     message_group будет равна None и в этом случае сообщение отправится,
    #     а иначе будем смотреть совпадает ли группа сообщения с одной из групп пользователя.
    #
    #     Args:
    #         user_group: группы пользователя
    #         message_group: группа сообщения
    #
    #     Returns:
    #         Вернёт ответ на вопрос можем ли посылать данное сообщение пользователю из исходя из групп.
    #     """
    #     if message_group is None:
    #         return True
    #
    #     return message_group in user_group

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
