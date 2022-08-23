"""Модуль содержит интерфейс для работы с Auth сервисом."""
import logging
from typing import Optional
from uuid import UUID

from pydantic import SecretStr

from config.settings import config
from email_formatter.models.http_responses import http
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
        authorization: SecretStr
    ) -> Optional[dict]:
        """
        Метод достаёт пользовательские данные из Auth.

        Args:
            destination_id: id пользователя, который нам нужен
            x_request_id: id запроса
            authorization: access токен доступа (пользовательские данные из Auth нельзя давать кому попало)

        Returns:
            Вернёт имя пользователя, почту и группы, в которых пользователь состоит.
        """
        url = f'{self.address}{config.auth_api.url_get_email}/{destination_id}'
        headers = {
            'Authorization': authorization.get_secret_value(),
            'X-Request-Id': x_request_id
        }

        async with await get_session() as session:
            result = await session.get(url, headers=headers)

        if result.status != http.ok.code:
            logger.error(f'Not Found email with id %s', destination_id)
            return None

        return await result.json()


logger = logging.getLogger(__name__)
auth_service = AuthService()
