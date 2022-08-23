import logging
from uuid import UUID

import aiohttp
from pydantic import SecretStr

from config.settings import config
from notifier_api.models.http_responses import http
from utils import aiohttp_session
from utils.aiohttp_session import get_session


class AuthService():

    def __init__(self):
        self.address = f'http://{config.auth_api.host}:{config.auth_api.port}'

    async def get_user_data_by_id(self, email_id: UUID, x_request_id: str, authorization: SecretStr):
        aiohttp_session.session = aiohttp.ClientSession()  # TODO: Точно тут?
        url = f'{self.address}{config.auth_api.url_get_email}/{email_id}'
        headers = {
            'Authorization': authorization.get_secret_value(),
            'X-Request-Id': x_request_id
        }

        async with await get_session() as session:
            result = await session.get(url, headers=headers)

        if result.status != http.ok.code:  # TODO: Не красиво, что http из другого сервиса.
            logger.error(f'Not Found email with id %s', email_id)
            return None

        return await result.json()


logger = logging.getLogger(__name__)
auth_service = AuthService()
