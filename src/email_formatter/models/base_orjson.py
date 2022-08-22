# Flake8: noqa
# type: ignore
"""Модуль содержит базовый класс."""
import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    """Быстрый orjson.dumps."""
    return orjson.dumps(v, default=default).decode()


class BaseOrjson(BaseModel):

    """Базовый класс с быстрой сериализации в json."""

    class Config:
        """
        Настройки pydantic.
        Подробнее см.
        https://pydantic-docs.helpmanual.io/usage/model_config/
        """
        allow_population_by_field_name = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps
