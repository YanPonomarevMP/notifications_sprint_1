from logging import getLogger

from fastapi import HTTPException, Depends

from db.storage.abstract_classes import AbstractDBClient
from db.storage.orm_factory import AsyncPGClient, get_db
from notifier_api.models.http_responses import http
from utils.custom_exceptions import DataBaseError


class HtmlTemplatesFactory:
    def __init__(self, orm: AbstractDBClient):
        self.orm = orm

    async def _execute(self, query):
        try:
            result = await self.orm.execute(query)

        except DataBaseError as error:
            raise HTTPException(status_code=http.backoff_error.code, detail=error.message)

        return result

    async def insert(self, query):

        result = await self._execute(query)

        if result:
            return f'Created at {result}'
        return 'Already exist'

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