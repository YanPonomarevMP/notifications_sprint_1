"""Модель содержит общие pydantic модели для всех ручек API."""
from typing import Optional
from uuid import UUID

from notifier_api.models.base_orjson import BaseOrjson


class IdempotencyKeyChecker(BaseOrjson):

    """
    Модель для проверки корректности UUID.
    Нужна для получения UUID из хэдера или другого невалидируемого источника.
    В случае ошибки она вызовет ValidationError,
    которое будет перехвачено валидатором основной модели.
    """

    idempotency_key: Optional[UUID]