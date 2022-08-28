from abc import ABC, abstractmethod
from typing import Union, Optional, List

from databases.interfaces import Record
from sqlalchemy.sql import Update, Select, Insert, Delete


class AbstractDBClient(ABC):
    """Абстрактный класс подключения к БД."""

    @abstractmethod
    async def start(self) -> None:
        """Метод создаёт соединение с БД."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Метод закрывает соединение с БД."""
        pass

    @abstractmethod
    async def execute(self, query: Union[Update, Select, Insert, Delete]) -> Optional[List[Record]]:
        """Метод выполняет запрос в БД."""
        pass
