"""Модуль содержит классы для асинхронной работы с БД."""
from typing import Union

import databases
from sqlalchemy.sql import Update, Select, Insert, Delete

from config.settings import config
from db.storage.abstract_classes import AbstractDBClient


class AsyncPGClient(AbstractDBClient):
    """Класс создаёт сессию для асинхронной работы с Postgres."""
    def __init__(self):
        user = config.pg.login.get_secret_value()
        password = config.pg.password.get_secret_value()
        host = config.pg.host
        db_name = config.pg.db_name
        self.session = databases.Database(f'postgresql://{user}:{password}@{host}/{db_name}')

    async def start(self) -> None:
        """Метод создаёт соединение с БД."""
        await self.session.connect()

    async def stop(self) -> None:
        """Метод закрывает соединение с БД."""
        await self.session.disconnect()

    async def execute(self, query: Union[Update, Select, Insert, Delete]):
        """
        Метод выполняет запрос в БД.
        Args:
            query: запрос к БД

        Returns:

        """
        answer = await self.session.execute(query)
        return answer
