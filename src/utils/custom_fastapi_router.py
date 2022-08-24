# Модуль содержит кастомный класс роутера для FastAPI.
from logging import getLogger
from typing import Callable, Tuple

from fastapi.routing import APIRoute
from fastapi import Request, Response

from notifier_api.models.access_log import AccessPath, XRequestID, Client


class LoggedRoute(APIRoute):
    """
    Класс реализует кастомный роутер, который позволит залогировать body запроса и ответа.
    Стандартный роутер и middleware этого сделать не дают.

    """

    def get_route_handler(self) -> Callable:
        """
        Метод вернёт кастомный route_handler вместо стандартного.

        Returns:
            Вернёт кастомный обработчик запроса с возможностью логирования.
        """

        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """
            Обработчик запроса с функцией логирования.

            Args:
                request: объект запроса FastAPI

            Returns:
                Возвращает результат обработки запроса.
            """

            # имя логгера, созданное из __name__ модуля будет здесь мало информативным,
            # поэтому мы создадим имя логгера из url запроса
            logger_name, request_log_message = await parse_request_for_logging(request)

            # Дополнительные заголовки нужны для логирования текущего запроса.
            await set_headers_for_logging(request, request_log_message, logger_name)

            response: Response = await original_route_handler(request)

            response_log_message = await parse_response_for_logging(response)
            logger = getLogger(logger_name)
            logger.info(f'{request_log_message} {response_log_message}')

            return response

        return custom_route_handler


async def parse_request_for_logging(request: Request) -> Tuple[str, str]:
    """
    Функция парсит информацию для логирования из запроса.

    Args:
        request: объект запроса FastAPI

    Returns:
        Кортеж с именем логгера и строкой сообщения для логирования запроса.
    """

    logger_name = AccessPath(name=request.scope['path'])
    x_request_id = XRequestID(value=request.scope['headers'])
    method = request.method
    client = Client(url=request.scope['client'])
    body = await request.json()

    return logger_name.name, f'{method} {client.url} {x_request_id.value} {body}'


async def parse_response_for_logging(response: Response) -> str:
    """
    Функция парсит информацию для логирования из ответа.

    Args:
        response: результат обработки запроса

    Returns:
        Строка для логирования ответа
    """

    status_code = response.status_code
    body = response.body.decode()

    return f'{status_code} {body}'


async def set_headers_for_logging(
    request: Request,
    log_message: str,
    logger_name: str
) -> None:
    """
    Функция установит дополнительные заголовки в запрос.

    Args:
        request: объект запроса FastAPI
        log_message: сообщение с логом запроса
        logger_name: имя логгера
    """
    request.scope['headers'].append((b'x-request-log-message', log_message.encode()))
    request.scope['headers'].append((b'x-request-logger-name', logger_name.encode()))
