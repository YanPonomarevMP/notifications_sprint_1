"""Модуль содержит интерфейс для работы с Auth сервисом."""
import logging
from typing import Optional
from uuid import UUID

from config.settings import config
from email_formatter.models.http_responses import http
from email_formatter.models.log import log_names
from utils.aiohttp_session import get_session


class AuthService:

    """Класс с интерфейсом для работы с Auth."""

    def __init__(self) -> None:

        """Конструктор."""

        self.address = f'http://{config.auth_api.host}:{config.auth_api.port}'

    async def get_user_data_by_id(
        self,
        destination_id: UUID,
        x_request_id: str,
    ) -> Optional[dict]:
        """
        Метод достаёт пользовательские данные из Auth.

        Args:
            destination_id: id пользователя, который нам нужен
            x_request_id: id запроса

        Returns:
            Вернёт имя пользователя, почту и группы, в которых пользователь состоит.
        """
        url = f'{self.address}{config.auth_api.url_get_email}/{destination_id}'
        headers = {'X-Request-Id': x_request_id}

        session = await get_session()
        result = await session.get(url, headers=headers)

        if result.status != http.ok.code:
            logger.error(log_names.error.failed_get, destination_id, 'Auth service')
            return None

        return await result.json()


logger = logging.getLogger('auth_service')
auth_service = AuthService()
