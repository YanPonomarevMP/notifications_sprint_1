"""Модуль содержит pydantic модели."""
from dataclasses import dataclass
from typing import Dict, Optional, Union
from uuid import UUID

from multidict import CIMultiDictProxy

from src.notifier_api.models.base_orjson import BaseOrjson  # type: ignore


@dataclass
class HTTPResponse:
    """Ответ API."""
    body: dict
    headers: CIMultiDictProxy[str]
    status: int

class Scenario(BaseOrjson):

    """Данные для запроса к API."""

    url: Optional[str]
    method: Optional[str]
    body: Optional[Dict] = None
    headers: Optional[Dict] = None
    params: Optional[Dict] = None
    expected_status: Optional[int]
    expected_body: Optional[Dict] = None
    check_body: bool = False
    check_len_body: bool = False
    check_len_str_body: bool = False



    class Config:
        """Настройка валидации при изменении значения поля."""

        validate_assignment = True
