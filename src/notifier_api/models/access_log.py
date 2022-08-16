"""Модуль содержит pydantic модель с данными запроса и ответа для access лога."""
from typing import Optional, Union, List

from models.base_orjson import BaseOrjson  # type: ignore
from pydantic import validator


class AccessPath(BaseOrjson):

    """Преобразование пути в имя логгера."""

    name: str

    @validator('name')
    def convert_path_to_name(cls, path: str) -> str:  # noqa: WPS110, N805
        """
        Метод преобразует путь из запроса в имя логгера.

        Args:
            path: значение пути, которое нужно преобразовать в имя

        Returns:
            Вернёт строку с именем логгера.
        """

        name = path.replace('/', '.')[1: -1]
        return f'access.{name}'


class XRequestID(BaseOrjson):

    """Парсит x_request_id из запроса."""

    value: Union[List[tuple], str]

    @validator('value')
    def parse_x_request_id_from_headers(cls, headers: List[tuple]) -> Optional[str]:  # noqa: WPS110, N805
        """
        Метод парсит x_request_id из списка хэдеров.

        Args:
            headers: список хэдеров

        Returns:
            Вернёт строку cо значением x_request_id.
        """

        for header in headers:
            if header[0] == b'x-request-id':
                return header[1].decode()
        return None


class Client(BaseOrjson):

    """Парсит клиента из запроса."""

    url: Union[tuple, str]

    @validator('url')
    def parse_x_request_id_from_headers(cls, url: str) -> str:  # noqa: WPS110, N805
        """
        Метод парсит url клиента из запроса.

        Args:
            url: кортеж с хостом и портом

        Returns:
            Вернёт строку c url.
        """
        host = url[0]
        port = url[1]

        return f'{host}:{port}'
