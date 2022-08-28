"""Модуль содержит классы для асинхронной работы с БД."""
from typing import Union, Optional, List

import databases
from databases.interfaces import Record
from sqlalchemy.sql import Update, Select, Insert, Delete

from config.settings import config
from db.storage.abstract_classes import AbstractDBClient
from utils.async_backoff import timeout_limiter


class AsyncPGClient(AbstractDBClient):

    """Класс создаёт сессию для асинхронной работы с Postgres."""

    def __init__(self) -> None:

        """Конструктор."""

        user = config.pg.login.get_secret_value()
        password = config.pg.password.get_secret_value()
        host = config.pg.host
        db_name = config.pg.db_name
        self.session = databases.Database(f'postgresql://{user}:{password}@{host}/{db_name}')  # noqa: WPS221

    async def start(self) -> None:
        """Метод создаёт соединение с БД."""
        await self.session.connect()

    async def stop(self) -> None:
        """Метод закрывает соединение с БД."""
        await self.session.disconnect()

    @timeout_limiter(max_timeout=10, logger_name='db.orm_factory.execute')
    async def execute(self, query: Union[Update, Select, Insert, Delete]) -> Optional[List[Record]]:
        """
        Метод выполняет запрос в БД.

        Args:
            query: запрос к БД

        Returns:
            Если запрос select — список полей, в противном случае ничего.
        """
        if query.is_select:
            return await self.session.fetch_all(query)
        return await self.session.execute(query)


db = AsyncPGClient()


async def get_db() -> AsyncPGClient:
    """Функция возвращает db объект."""
    return db  # type: ignore
