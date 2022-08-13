"""Модуль содержит абстрактные классы."""
from abc import ABC, abstractmethod
from typing import Optional, Union, Callable


class AbstractMessageBroker(ABC):

    """Класс с интерфейсом брокера сообщений."""

    @abstractmethod
    async def consume(self, queue_name: str, callback: Callable) -> None:
        """
        Метод обрабатывает сообщения функцией callback из очереди с названием queue_name.

        Args:
            queue_name: название очереди, из которой хотим получить данные
            callback: функция, которая будет работать с итератором `def func(iterator: AsyncIterator)`
        """
        pass

    @abstractmethod
    async def publish(
        self,
        message_body: bytes,
        queue_name: str,
        exchange_name: str,
        message_headers: Optional[dict] = None,
        expiration: Optional[Union[int, float]] = None
    ) -> None:
        """
        Метод складывает сообщение в очередь.

        Args:
            message_body: содержимое сообщения
            expiration: ttl сообщения, указывается в секундах
            queue_name: название очереди, в которую нужно отправить сообщение
            exchange_name: название обменника
            message_headers: заголовок сообщения (сюда нужно вставить x-request-id)
        """
        pass
