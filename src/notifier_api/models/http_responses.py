# type: ignore
"""Модуль с различными HTTP статусами."""
from http import HTTPStatus
from typing import Dict

from notifier_api.models.base_orjson import BaseOrjson

code_200 = HTTPStatus.OK.value
code_400 = HTTPStatus.BAD_REQUEST.value
code_429 = HTTPStatus.TOO_MANY_REQUESTS.value
code_401 = HTTPStatus.UNAUTHORIZED.value
code_403 = HTTPStatus.FORBIDDEN.value


class Response(BaseOrjson):

    """Ответ API и status code API."""

    message: Dict
    code: int


class HTTPResponses(BaseOrjson):

    """Все варианты ответов API, собранные в одном месте."""

    ok: Response = Response(message={'msg': 'OK'}, code=code_200)
    bad_request: Response = Response(message={'msg': 'Bad request'}, code=code_400)
    unauthorized: Response = Response(message={'msg': 'Authorization required'}, code=code_401)
    forbidden: Response = Response(message={'msg': 'Forbidden'}, code=code_403)
    request_id_required: Response = Response(message={'msg': 'Х-Request-id required'}, code=code_400)
    too_many_requests: Response = Response(message={'msg': 'too many requests'}, code=code_429)


http = HTTPResponses()
