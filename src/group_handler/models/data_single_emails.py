"""Модуль содержит pydantic классы."""
from typing import Dict, Optional
from uuid import UUID

from group_handler.models.base_config import BaseConfigModel


class DataSingleEmails(BaseConfigModel):

    """Данные для вставки в SingleEmails."""

    id: Optional[UUID]
    source: str
    destination_id: UUID
    template_id: UUID
    group_id: Optional[UUID]
    subject: str
    message: Dict
    delay: int = 0
