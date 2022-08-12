# type: ignore
"""Модуль с различными HTTP статусами."""
from http import HTTPStatus
from typing import Dict

from notifier_api.models.base_orjson import BaseOrjson

code_200 = HTTPStatus.OK.value
code_400 = HTTPStatus.BAD_REQUEST.value
code_429 = HTTPStatus.TOO_MANY_REQUESTS.value


class Response(BaseOrjson):

    """Ответ API и status code API."""

    message: Dict
    code: int


class HTTPResponses(BaseOrjson):

    """Все варианты ответов API, собранные в одном месте."""

    ok: Response = Response(message={'msg': 'OK'}, code=code_200)
    bad_request: Response = Response(message={'msg': 'Bad request. Perhaps request header is incorrect'}, code=code_400)
    request_id_required: Response = Response(message={'msg': 'Bad request. Request id is required'}, code=code_400)
    too_many_requests: Response = Response(message={'msg': 'too many requests'}, code=code_429)


http = HTTPResponses()
