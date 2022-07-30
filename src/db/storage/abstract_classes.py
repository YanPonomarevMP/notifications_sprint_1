from abc import ABC, abstractmethod


class AbstractDBClient(ABC):
    """Абстрактный класс подключения к БД."""

    @abstractmethod
    async def start(self):
        """Метод создаёт соединение с БД."""
        pass

    @abstractmethod
    async def stop(self):
        """Метод закрывает соединение с БД."""
        pass
