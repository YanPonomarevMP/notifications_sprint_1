from logging import getLogger

from fastapi import HTTPException, Depends

from db.storage.abstract_classes import AbstractDBClient
from db.storage.orm_factory import AsyncPGClient, get_db
from notifier_api.models.http_responses import http
from notifier_api.services.base_execute_factory import BaseExecuteFactory
from utils.custom_exceptions import DataBaseError


class HtmlTemplatesFactory(BaseExecuteFactory):

    async def insert(self, query):

        result = await self._execute(query)

        if result:
            return f'Created at {result}'
        return 'Already exist'

    async def update(self, query, response):

        result = await self._execute(query)

        if result:
            return f'Updated at {result}'
        response.status_code = http.not_found.code
        return 'Not found'

    async def delete(self, query, response):

        result = await self._execute(query)

        if result:
            return f'Deleted at {result}'
        response.status_code = http.not_found.code
        return 'Not found'

    async def select(self, query, response):

        templates_selected = []
        result = await self._execute(query)

        if result:
            for row in result:
                templates_selected.append(dict(row._mapping))  # noqa: WPS437
            return 'Successfully selected', templates_selected

        response.status_code = http.not_found.code
        return 'Not found', templates_selected


async def get_html_templates_factory(database: AsyncPGClient = Depends(get_db)):
    return HtmlTemplatesFactory(orm=database)