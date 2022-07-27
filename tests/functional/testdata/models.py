"""Модуль содержит pydantic модели."""
from dataclasses import dataclass

from multidict import CIMultiDictProxy


@dataclass
class HTTPResponse:
    """Ответ API."""
    body: dict
    headers: CIMultiDictProxy[str]
    status: int
