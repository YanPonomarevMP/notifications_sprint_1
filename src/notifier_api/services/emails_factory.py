from typing import Union, Optional

from fastapi import HTTPException, Depends, Response

from db.message_brokers.rabbit_message_broker import message_broker_factory
from db.storage.abstract_classes import AbstractDBClient
from db.storage.orm_factory import AsyncPGClient, get_db
from notifier_api.models.http_responses import http  # type: ignore
from notifier_api.models.message_broker_models import MessageBrokerData
from utils.custom_exceptions import DataBaseError

from sqlalchemy import update, select
from sqlalchemy.dialects.postgresql import insert

class EmailsFactory:
    def __init__(self, orm: AbstractDBClient):
        self.orm = orm

    async def _execute(self, query: Union[update, select, insert], message_to_broker: MessageBrokerData = None)  -> Optional[list]:
        try:
            result_db = await self.orm.execute(query)
            if result_db and message_to_broker:
                if not await message_broker_factory.publish(**message_to_broker.dict()):
                    raise DataBaseError(
                        db_name='message_broker',
                        message='Message not published',
                        error_type='Broker did not receive Basic.Ack',
                        critical=True
                    )

        except DataBaseError as error:
            raise HTTPException(status_code=http.backoff_error.code, detail=error.message)

        return result_db

    async def insert(self, query: Union[update, select, insert], message_to_broker: MessageBrokerData = None) -> str:

        result = await self._execute(query, message_to_broker)

        if result:
            return f'Created at {result}'
        return 'Already exist'

    async def update(self, query: Union[update, select, insert], response: Response) -> str:

        result = await self._execute(query)

        if result:
            return f'Updated at {result}'
        response.status_code = http.not_found.code
        return 'Not found'

    async def delete(self, query: Union[update, select, insert], response: Response) -> str:

        result = await self._execute(query)

        if result:
            return f'Deleted at {result}'
        response.status_code = http.not_found.code
        return 'Not found'

    async def select(self, query: select, response, selected_model) -> tuple:

        selected_data = []
        result = await self._execute(query)

        if result:
            for row in result:
                selected_data.append(selected_model(**dict(row._mapping)))  # noqa: WPS437
            return 'Successfully selected', selected_data

        response.status_code = http.not_found.code
        return 'Not found', selected_data


async def get_emails_factory(database: AsyncPGClient = Depends(get_db)) -> EmailsFactory:
    return EmailsFactory(orm=database)
