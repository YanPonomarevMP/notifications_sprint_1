from logging import getLogger
from typing import Callable, Tuple

from fastapi.routing import APIRoute
from fastapi import Request, Response

from notifier_api.models.access_log import AccessPath, XRequestID, Client


class LoggedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:

            logger_name, request_log_message = await parse_request_for_logging(request)
            request.scope['headers'].append((b'x-request-log-message', request_log_message.encode()))
            request.scope['headers'].append((b'x-request-logger-name', logger_name.encode()))

            response: Response = await original_route_handler(request)

            response_log_message = await parse_response_for_logging(response)
            logger = getLogger(logger_name)
            logger.info(f'{request_log_message} {response_log_message}')

            return response

        return custom_route_handler


async def parse_request_for_logging(request: Request) -> Tuple[str, str]:

    logger_name = AccessPath(name=request.scope['path'])
    x_request_id = XRequestID(value=request.scope['headers'])
    method = request.method
    client = Client(url=request.scope['client'])
    body = await request.json()

    return logger_name.name, f'{method} {client.url} {x_request_id.value} {body}'


async def parse_response_for_logging(response: Response) -> str:

    status_code = response.status_code
    body = response.body.decode()

    return f'{status_code} {body}'
