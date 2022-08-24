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
    created: Response = Response(message=status.CREATED.phrase, code=status.CREATED.value)
    bad_request: Response = Response(message=status.BAD_REQUEST.phrase, code=status.BAD_REQUEST.value)
    unauthorized: Response = Response(message=status.UNAUTHORIZED.phrase, code=status.UNAUTHORIZED.value)
    forbidden: Response = Response(message=status.FORBIDDEN.phrase, code=status.FORBIDDEN.value)
    request_id_required: Response = Response(message='X-Request-id required', code=status.BAD_REQUEST.value)
    too_many_requests: Response = Response(message=status.TOO_MANY_REQUESTS.phrase, code=status.TOO_MANY_REQUESTS.value)
    request_validation_error: Response = Response(message='Validation error', code=status.UNPROCESSABLE_ENTITY.value)


http = HTTPResponses()
