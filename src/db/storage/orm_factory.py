"""Модуль содержит классы для асинхронной работы с БД."""
import databases

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

    async def start(self):
        """Метод создаёт соединение с БД."""
        await self.session.connect()

    async def stop(self):
        """Метод закрывает соединение с БД."""
        await self.session.disconnect()


# class Storage:
#
#     def __init__(self, client):
