# type: ignore
"""Модуль с различными HTTP статусами."""
from http import HTTPStatus as status
from typing import Dict, Union

from notifier_api.models.base_orjson import BaseOrjson


class Response(BaseOrjson):

    """Ответ API и status code API."""

    message: Union[Dict, str]
    code: int


class HTTPResponses(BaseOrjson):

    """Все варианты ответов API, собранные в одном месте."""

    ok: Response = Response(message=status.OK.phrase, code=status.OK.value)


http = HTTPResponses()
