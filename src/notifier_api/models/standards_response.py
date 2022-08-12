"""Модуль содержит pydantic модели со стандартами входных/выходных данных API."""
from typing import Optional, List

from models.base_orjson import BaseOrjson  # type: ignore
from models.http_responses import Response  # type: ignore


class ResponseData(BaseOrjson):

    """Данные ответа на запрос."""

    response: List


class BaseUGCResponse(BaseOrjson):

    """Формат ответа UGC API."""

    data: Optional[ResponseData]
    metadata: Response
