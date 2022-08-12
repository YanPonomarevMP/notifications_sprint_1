"""Модуль содержит pydantic модель с данными из токена."""
from typing import Optional

from models.base_orjson import BaseOrjson  # type: ignore


class AccessTokenData(BaseOrjson):

    """Все возможные данные из токена."""

    iat: str
    ttl: int
    user_id: str
    user_roles: Optional[list]
    user_fingerprint: Optional[str]
    access_token_id: str
    refresh_token_id: str
