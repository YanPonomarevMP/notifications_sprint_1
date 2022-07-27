"""Модуль содержит настройки для тестов."""
from pydantic import BaseSettings, BaseModel, Field


class UGCSettings(BaseModel):

    """Настройки UGC для тестов."""

    url: str = Field('http://127.0.0.1:8000', env='UGC_URL')
    prefix: str = '/v1'
    handle_events_post: str = '/events/'


class TestSettings(BaseSettings):

    """Все настройки для тестов."""

    ugc_api: UGCSettings = UGCSettings()


settings = TestSettings()
