"""Модель содержит pydantic модели для RawData из DB."""
from typing import Union, Optional
from uuid import UUID

import orjson
from pydantic import validator

from email_formatter.models.base_config import BaseConfigModel  # type: ignore


class RawDataDB(BaseConfigModel):

    """Класс с «сырыми» данными из DB."""

    template_id: UUID
    destination_id: UUID
    message: dict
    group_id: Optional[UUID]
    source: str
    subject: str
