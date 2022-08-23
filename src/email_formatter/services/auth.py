import logging
from uuid import UUID

import aiohttp

from config.settings import config
from notifier_api.models.http_responses import http
from utils import aiohttp_session
from utils.aiohttp_session import get_session


class AuthService():

    async def get_email_by_id(self, email_id: UUID, x_request_id: str):
        headers = {
            'Authorization': config.auth_api.access_token.get_secret_value(),
            'X-Request-Id': x_request_id
        }
        aiohttp_session.session = aiohttp.ClientSession()

        session = await get_session()
        url = f'http://{config.auth_api.host}:{config.auth_api.port}{config.auth_api.url_get_email}/{email_id}'  # noqa: WPS237

        response = await session.get(url, headers=headers)
        if response.status != http.ok.code:
            logger.error(f'{http.forbidden.message} email with id %s', email_id)
            return None
        return await response.json()


logger = logging.getLogger(__name__)
auth_service = AuthService()
