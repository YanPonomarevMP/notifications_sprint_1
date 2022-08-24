"""Модуль содержит настройки приложения."""
from logging import config as logging_config

from pydantic import BaseSettings, SecretStr

from config.logging_settings import LOGGING
from security.vault_app_config import vault

logging_config.dictConfig(LOGGING)


class RabbitAlifeQueues(BaseSettings):

    """
    Настройки «живых» очередей.
    Тут хранятся имена очередей, которые будут слушать consumer-ы.
    """

    queue_raw_single_messages: str = vault.get_secret('queue_raw_single_messages')
    queue_raw_group_messages: str = vault.get_secret('queue_raw_group_messages')


class RabbitSettings(BaseSettings):

    """Настройки RabbitMQ."""

    host: str = vault.get_secret('rabbit_host')
    port: int = vault.get_secret('rabbit_port')
    login: SecretStr = vault.get_secret('rabbit_login')
    password: SecretStr = vault.get_secret('rabbit_password')
    queue_waiting_depart: str = vault.get_secret('queue_waiting_depart')
    queue_waiting_retry: str = vault.get_secret('queue_waiting_retry')
    exchange_incoming: str = vault.get_secret('exchange_incoming')
    exchange_sorter: str = vault.get_secret('exchange_sorter')
    exchange_retry: str = vault.get_secret('exchange_retry')
    default_message_ttl_ms: int = vault.get_secret('default_message_ttl_ms')
    max_retry_count: int = vault.get_secret('max_retry_count')
    alife_queues: RabbitAlifeQueues = RabbitAlifeQueues()


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

    host: str = vault.get_secret('fast_api_host')
    port: int = vault.get_secret('fast_api_port')
    swagger_docs: SettingsSwaggerDocs = SettingsSwaggerDocs()


class SettingsAuthAPI(BaseSettings):

    """Класс настроек Auth сервера."""

    host: str = vault.get_secret('auth_api_host')
    port: int = vault.get_secret('auth_api_port')
    url_check_token: str = vault.get_secret('url_check_token')
    access_token: SecretStr = vault.get_secret('auth_api_access_token')
    url_get_email: str = vault.get_secret('url_get_email')


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
