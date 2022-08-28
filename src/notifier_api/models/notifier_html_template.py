"""Модель содержит pydantic модели входящих данных ручки /html_templates."""
from datetime import datetime
from typing import Optional, Union, List, Dict
from uuid import UUID

from models.base_orjson import BaseOrjson  # type: ignore


class HtmlTemplatesRequest(BaseOrjson):

    """Данные, поступившие от клиента."""

    title: str
    template: str


class HtmlTemplatesQuery(BaseOrjson):

    """Модель для работы с данными при обработке запроса."""

    id: Optional[UUID]
    title: Optional[str]
    template: Optional[str]
    templates_selected: Optional[List[Dict]]
    msg: Optional[Union[datetime, str]]

    class Config:
        """Настройка валидации при изменении значения поля."""

        validate_assignment = True


class HtmlTemplatesResponse(BaseOrjson):

    """Формат ответа UGC API."""

    id: Optional[UUID]
    msg: Optional[Union[datetime, str]]


class HtmlTemplateSelected(BaseOrjson):

    """Модель для работы с данными при обработке запроса."""

    id: Optional[UUID]
    title: Optional[str]
    template: Optional[str]


class HtmlTemplatesResponseSelected(BaseOrjson):

    """Формат ответа UGC API."""

    msg: Optional[str]
    templates_selected: Optional[List[Dict]]
