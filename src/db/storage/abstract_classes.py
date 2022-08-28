from abc import ABC, abstractmethod


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
    async def execute(self, query) -> None:
        """Метод выполняет запрос в БД."""
        pass
