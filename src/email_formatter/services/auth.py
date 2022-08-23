import logging
from uuid import UUID

import aiohttp

from config.settings import config
from notifier_api.models.http_responses import http
from utils import aiohttp_session
from utils.aiohttp_session import get_session


class AuthService():

    def __init__(self):
        self.address = f'http://{config.auth_api.host}:{config.auth_api.port}'
        aiohttp_session.session = aiohttp.ClientSession()

    async def get_email_by_id(self, email_id: UUID, x_request_id: str):

        url = f'{self.address}{config.auth_api.url_get_email}/{email_id}'
        headers = {
            'Authorization': config.auth_api.access_token.get_secret_value(),
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
