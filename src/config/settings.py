"""Модуль содержит настройки приложения."""
import os
from pydantic import BaseSettings, SecretStr

from config.fast_api_logging import LOGGING
from security.vault_app_config import vault


class RabbitSettings(BaseSettings):

    """Настройки RabbitMQ."""

    host: str = vault.get_secret('rabbit_host')
    port: int = vault.get_secret('rabbit_port')
    login: SecretStr = vault.get_secret('rabbit_login')
    password: SecretStr = vault.get_secret('rabbit_password')


class PostgresSettings(BaseSettings):
    login: SecretStr = vault.get_secret('pg_user')  # имя поля user пересекается с переменной окружения user
    password: SecretStr = vault.get_secret('pg_password')
    host: str = vault.get_secret('pg_host')
    db_name: str = vault.get_secret('pg_db_name')


class SettingsSwaggerDocs(BaseSettings):

    """Класс настроек swagger документации."""

    title: str = vault.get_secret('fast_api_swagger_title')
    description: str = vault.get_secret('fast_api_swagger_description')
    version: str = vault.get_secret('fast_api_swagger_version')
    docs_url: str = vault.get_secret('fast_api_swagger_docs_url')
    openapi_url: str = vault.get_secret('fast_api_swagger_openapi_url')


class SettingsFastAPI(BaseSettings):

    """Класс настроек FastAPI."""

    logging: dict = LOGGING
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    host: str = vault.get_secret('fast_api_host')
    port: int = vault.get_secret('fast_api_port')
    swagger_docs: SettingsSwaggerDocs = SettingsSwaggerDocs()


class SettingsAuthAPI(BaseSettings):

    """Класс настроек Auth сервера."""

    host: str = vault.get_secret('auth_api_host')
    port: int = vault.get_secret('auth_api_port')
    url_check_token: str = '/v1/back/check_token'
    access_token: SecretStr = vault.get_secret('auth_api_access_token')


class SettingsJaeger(BaseSettings):

    """Класс настроек Jaeger."""

    host: str = vault.get_secret('jaeger_host')
    port: int = vault.get_secret('jaeger_port')


class SettingsRedis(BaseSettings):

    """Класс настроек Redis."""

    host: str = vault.get_secret('redis_host')
    port: int = vault.get_secret('redis_port')



class Config(BaseSettings):

    """Класс с конфигурацией проекта."""

    rabbit_mq: RabbitSettings = RabbitSettings()
    pg: PostgresSettings = PostgresSettings()
    fast_api: SettingsFastAPI = SettingsFastAPI()
    auth_api: SettingsAuthAPI = SettingsAuthAPI()
    jaeger: SettingsJaeger = SettingsJaeger()
    redis: SettingsRedis = SettingsRedis()


config = Config()
