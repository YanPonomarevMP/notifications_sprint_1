"""Модуль содержит класс с интерфейсом для работы с Emails."""
from typing import Union, Optional, Callable

from fastapi import HTTPException, Depends, Response
from sqlalchemy.sql import Select, Update, Insert

from db.message_brokers.rabbit_message_broker import message_broker_factory
from db.storage.abstract_classes import AbstractDBClient
from db.storage.orm_factory import AsyncPGClient, get_db
from notifier_api.models.http_responses import http  # type: ignore
from notifier_api.models.message_broker_models import MessageBrokerData
from utils.custom_exceptions import DataBaseError


class EmailsFactory:

    """Класс с интерфейсом для работы с Emails."""

    def __init__(self, orm: AbstractDBClient) -> None:
        """
        Конструктор.

        Args:
            orm: класс для низкоуровневой работой с БД
        """
        self.orm = orm

    async def insert(
        self,
        query: Union[Update, Select, Insert],
        message_to_broker: Optional[MessageBrokerData] = None
    ) -> str:
        """
        Метод выполняет insert.

        Args:
            query: запрос
            message_to_broker: сообщение для брокера

        Returns:
            Вернёт сообщение для API.
        """
        result = await self._execute(query, message_to_broker)

        if result:
            return f'Created at {result}'
        return 'Already exist'

    async def update(self, query: Union[Update, Select, Insert], response: Response) -> str:
        """
        Метод выполняет update.

        Args:
            query: запрос
            response: ответ

        Returns:
            Вернёт сообщение для API.
        """
        result = await self._execute(query)

        if result:
            return f'Updated at {result}'
        response.status_code = http.not_found.code
        return 'Not found'

    async def delete(self, query: Union[Update, Select, Insert], response: Response) -> str:
        """
        Метод выполняет delete.

        Args:
            query: запрос
            response: ответ

        Returns:
            Вернёт сообщение для API.
        """
        result = await self._execute(query)

        if result:
            return f'Deleted at {result}'
        response.status_code = http.not_found.code
        return 'Not found'

    async def select(self, query: Select, response: Response, selected_model: Callable) -> tuple:
        """
        Метод выполняет select.

        Args:
            query: запрос
            response: ответ
            selected_model: pydantic модель

        Returns:
            Вернёт сообщение для API и данные.
        """
        selected_data = []
        result = await self._execute(query)

        if result:
            for row in result:
                selected_data.append(selected_model(**dict(row._mapping)))  # noqa: WPS437
            return 'Successfully selected', selected_data

        response.status_code = http.not_found.code
        return 'Not found', selected_data

    async def _execute(  # noqa: WPS231
        self,
        query: Union[Update, Select, Insert],
        message_to_broker: Optional[MessageBrokerData] = None
    ) -> Optional[list]:
        """
        Метод выполняет запрос.

        Args:
            query: запрос
            message_to_broker: сообщение для брокера

        Returns:
            Вернёт результат запроса.

        Raises:
            HTTPException: если что-то пошло не так и в брокер записать не удалось
        """
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


async def get_emails_factory(database: AsyncPGClient = Depends(get_db)) -> EmailsFactory:

    """
    Метод создаёт EmailsFactory.

    Args:
        database: клиент для работы с БД

    Returns:
        Вернёт pydantic модель EmailsFactory.
    """

    return EmailsFactory(orm=database)
