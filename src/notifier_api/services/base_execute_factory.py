from fastapi import HTTPException

from db.storage.abstract_classes import AbstractDBClient
from notifier_api.models.http_responses import http
from utils.custom_exceptions import DataBaseError


class BaseExecuteFactory:

    def __init__(self, orm: AbstractDBClient):
        self.orm = orm

    async def _execute(self, query):
        try:
            result = await self.orm.execute(query)

        except DataBaseError as error:
            raise HTTPException(status_code=http.backoff_error.code, detail=error.message)

        return result