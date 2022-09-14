"""Модуль содержит настройки приложения."""
from logging import config as logging_config

from pydantic import BaseSettings, SecretStr

from config.logging_settings import LOGGING
from security.env_config import env
from security.vault_app_config import VaultAppConfig
from security.vault_client import client

# Режим разработки для запуска приложения с локальными настройками dev_mode_value вместо значений из vault
# Удобно использовать для быстрого переключения настроек между compose и локальной машиной,
# меняя хосты контейнеров
DEV_MODE = True

logging_config.dictConfig(LOGGING)
vault = VaultAppConfig(vault_client=client, app_name=env.vault_app_name, dev_mode=DEV_MODE)


class SMTPSettings(BaseSettings):

    """Настройки SMTP."""

    host: str = vault.get_setting('smtp_host')
    port: int = vault.get_setting('smtp_port')
    login: SecretStr = vault.get_setting('smtp_login')
    password: SecretStr = vault.get_setting('smtp_password')
    email_address: str = vault.get_setting('smtp_email_address')


class RabbitSettings(BaseSettings):

    """Настройки RabbitMQ."""

    host: str = vault.get_setting('rabbit_host')
    port: int = vault.get_setting('rabbit_port')
    login: SecretStr = vault.get_setting('rabbit_login')
    password: SecretStr = vault.get_setting('rabbit_password')
    queue_waiting_depart: str = vault.get_setting('queue_waiting_depart')
    queue_waiting_retry: str = vault.get_setting('queue_waiting_retry')
    exchange_incoming: str = vault.get_setting('exchange_incoming')
    exchange_sorter: str = vault.get_setting('exchange_sorter')
    exchange_retry: str = vault.get_setting('exchange_retry')
    default_message_ttl_ms: int = vault.get_setting('default_message_ttl_ms')
    max_retry_count: int = vault.get_setting('max_retry_count')

    queue_raw_single_messages: str = vault.get_setting('queue_raw_single_messages')
    queue_raw_group_messages: str = vault.get_setting('queue_raw_group_messages')
    queue_formatted_single_messages: str = vault.get_setting('queue_formatted_single_messages')


class PostgresSettings(BaseSettings):

    """Настройки postgres."""

    login: SecretStr = vault.get_setting('pg_user')  # имя поля user пересекается с переменной окружения user
    password: SecretStr = vault.get_setting('pg_password')
    host: str = vault.get_setting('pg_host')
    db_name: str = vault.get_setting('pg_db_name')


class SettingsSwaggerDocs(BaseSettings):

    """Класс настроек swagger документации."""

    title: str = vault.get_setting('fast_api_swagger_title')
    description: str = vault.get_setting('fast_api_swagger_description')
    version: str = vault.get_setting('fast_api_swagger_version')
    docs_url: str = vault.get_setting('fast_api_swagger_docs_url')
    openapi_url: str = vault.get_setting('fast_api_swagger_openapi_url')


class SettingsFastAPI(BaseSettings):

    """Класс настроек FastAPI."""

    host: str = vault.get_setting('fast_api_host')
    port: int = vault.get_setting('fast_api_port')
    swagger_docs: SettingsSwaggerDocs = SettingsSwaggerDocs()


class SettingsAuthAPI(BaseSettings):

    """Класс настроек Auth сервера."""

    host: str = vault.get_setting('auth_api_host')
    port: int = vault.get_setting('auth_api_port')
    url_check_token: str = vault.get_setting('url_check_token')
    access_token: SecretStr = vault.get_setting('auth_api_access_token')
    url_get_email: str = vault.get_setting('url_get_email')
    url_get_by_group: str = vault.get_setting('url_get_by_group')


class SettingsJaeger(BaseSettings):

    """Класс настроек Jaeger."""

    host: str = vault.get_setting('jaeger_host')
    port: int = vault.get_setting('jaeger_port')


class SettingsRedis(BaseSettings):

    """Класс настроек Redis."""

    host: str = vault.get_setting('redis_host')
    port: int = vault.get_setting('redis_port')


class Config(BaseSettings):

    """Класс с конфигурацией проекта."""

    rabbit_mq: RabbitSettings = RabbitSettings()
    pg: PostgresSettings = PostgresSettings()
    fast_api: SettingsFastAPI = SettingsFastAPI()
    auth_api: SettingsAuthAPI = SettingsAuthAPI()
    jaeger: SettingsJaeger = SettingsJaeger()
    redis: SettingsRedis = SettingsRedis()
    smtp: SMTPSettings = SMTPSettings()


config = Config()
