"""Модуль содержит настройки для тестов."""
from pydantic import BaseSettings, BaseModel, Field


class NotifierTstSettings(BaseModel):

    """Настройки UGC для тестов."""

    url: str = Field('http://127.0.0.1:8000', env='UGC_URL')
    prefix: str = '/v1'



class TestSettings(BaseSettings):

    """Все настройки для тестов."""

    notifier_test_api: NotifierTstSettings = NotifierTstSettings()


settings = TestSettings()
print()