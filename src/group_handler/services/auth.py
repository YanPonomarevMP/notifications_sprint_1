"""Модуль содержит интерфейс для работы с Auth сервисом."""
import logging
from typing import Optional, List
from uuid import UUID

from config.settings import config
from email_formatter.models.http_responses import http  # type: ignore
from email_formatter.models.log import log_names
from group_handler.models.all_data import AuthData
from utils.aiohttp_session import get_session


class AuthService:

    """Класс с интерфейсом для работы с Auth."""

    def __init__(self) -> None:

        """Конструктор."""

        self.address = f'http://{config.auth_api.host}:{config.auth_api.port}'  # noqa: WPS237

    async def get_by_group(
        self,
        destination_id: UUID,
        x_request_id: str
    ) -> List[AuthData]:
        """
        Метод достаёт пользовательские данные из Auth.

        Args:
            destination_id: id пользователя, который нам нужен
            x_request_id: id запроса

        Returns:
            Вернёт имя пользователя, почту и группы, в которых пользователь состоит.
        """
        url = f'{self.address}{config.auth_api.url_get_by_group}/{destination_id}'  # noqa: WPS237
        headers = {'X-Request-Id': x_request_id}
        session = await get_session()
        result = await session.get(url, headers=headers)

        if result.status != http.ok.code:
            # logger.error(log_names.error.failed_get, destination_id, 'Auth service')
            return []

        # logger.info(log_names.info.success_get, destination_id, 'Auth service')
        users_data = await result.json()
        return [AuthData(**user) for user in users_data]


logger = logging.getLogger('email_formatter.auth_service')
auth_service = AuthService()
