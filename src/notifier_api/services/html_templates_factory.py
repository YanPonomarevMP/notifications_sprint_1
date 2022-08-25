from logging import getLogger

from fastapi import HTTPException, Depends

from db.storage.abstract_classes import AbstractDBClient
from db.storage.orm_factory import AsyncPGClient, get_db
from notifier_api.models.http_responses import http
from utils.custom_exceptions import DataBaseError


class HtmlTemplatesFactory:
    def __init__(self, orm: AbstractDBClient):
        self.orm = orm

    async def execute(
        self,
        query,
    ):
        try:
            result = await self.orm.execute(query)

        except DataBaseError as error:
            raise HTTPException(status_code=http.backoff_error.code, detail=error.message)

        if result:
            return f'Executed at {result}'
        return 'Has been done before'


async def get_html_templates_factory(database: AsyncPGClient = Depends(get_db)):
    return HtmlTemplatesFactory(orm=database)