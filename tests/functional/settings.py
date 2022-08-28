"""Модуль содержит настройки для тестов."""
import uuid

from pydantic import BaseSettings, BaseModel, Field


class ApiSettings(BaseModel):

    """Настройки API для тестов."""

    url: str = Field('http://127.0.0.1:8000', env='UGC_URL')
    prefix: str = '/v1'


class Constants(BaseModel):

    """Константы для тестов."""
    correct_jwt_token: str = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY1NDAwNzE5NiwianRpIjoiMjNlY2I4ZjMtNDRlNS00ZTMyLWEwMjYtYzczNGYzZGY3NTMxIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOnsiaWF0IjoiVHVlLCAzMSBNYXkgMjAyMiAxNDoyNjozNiBHTVQiLCJ0dGwiOjQzMjAwMCwidXNlcl9pZCI6ImNmOThmZTEyLTBkODYtNDY3ZC1iODVkLTI3NmFmNDE1ZjMxMyIsImFjY2Vzc190b2tlbl9pZCI6IjkzNmVmYTVlLTBhZmItNDQ2OC1iYTFmLWIxMTRiNmU1ZWZhYiIsInJlZnJlc2hfdG9rZW5faWQiOiI2OThjMmRmNS0zYTBiLTRhOWItODk0ZC01NzVhNmE2M2FiZWMifSwibmJmIjoxNjU0MDA3MTk2LCJleHAiOjE2NTQ0MzkxOTZ9.-cKVzkM8sbfwfPisvsVVfYi-LGQv7koV6oRIUnXT7JI'
    incorrect_jwt_token: str = 'Bullshit'
    correct_uuid: str = str(uuid.uuid4())
    not_used_uuid: str = str(uuid.uuid4())
    incorrect_uuid: str = '3aec01aa-3033-4281-964a-5e035e7aac8'

class TestSettings(BaseSettings):

    """Все настройки для тестов."""

    api: ApiSettings = ApiSettings()
    const: Constants = Constants()


settings = TestSettings()
