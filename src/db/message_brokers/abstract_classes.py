"""Модуль содержит абстрактные классы."""
from abc import ABC, abstractmethod
from typing import Optional, Union, Callable

from pamqp.commands import Basic


class AbstractMessageBroker(ABC):

    """Класс с интерфейсом брокера сообщений."""

    @abstractmethod
    async def consume(self, queue_name: str, callback: Callable) -> None:
        """
        Метод обрабатывает сообщения функцией callback из очереди с названием queue_name.

        Args:
            queue_name: название очереди, из которой хотим получить данные
            callback: функция, которая будет обрабатывать сообщения
        """
        pass

    @abstractmethod
    async def publish(
        self,
        message_body: bytes,
        queue_name: str,
        message_headers: Optional[dict] = None,
        delay: Union[int, float] = 0
    ) -> Union[Basic.Ack, Basic.Nack, Basic.Reject, None]:
        """
        Метод складывает сообщение в очередь.

        Args:
            message_body: содержимое сообщения
            delay: ttl сообщения, указывается в секундах
            queue_name: название очереди, в которую нужно отправить сообщение
            message_headers: заголовок сообщения (сюда нужно вставить x-request-id)

        Returns:
            Вернёт ответ на вопрос была ли запись успешно добавлена
        """
        pass

    @abstractmethod
    async def idempotency_startup(self) -> None:
        """
        Метод для конфигурации базовой архитектуры RabbitMQ.
        Использовать ОДИН раз при старте сервиса.

        Можно конечно и больше,
        но этот метод все действие выполнит только один раз,
        следовательно, никакого резона вызывать его более одного раза нет.
        """
        pass
