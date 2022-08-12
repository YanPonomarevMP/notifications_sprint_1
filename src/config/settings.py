"""Модуль содержит настройки приложения."""
from pydantic import BaseSettings, SecretStr

from security.vault_app_config import vault


class MessageRabbitSettings(BaseSettings):

    """Настройки сообщений для брокера."""

    expiration: int = 30_000  # 30 минут. Указываем миллисекунды.


class RabbitSettings(BaseSettings):

    """Настройки RabbitMQ."""

    host: str = vault.get_secret('rabbit_host')
    port: int = vault.get_secret('rabbit_port')
    login: SecretStr = vault.get_secret('rabbit_login')
    password: SecretStr = vault.get_secret('rabbit_password')
    message: MessageRabbitSettings = MessageRabbitSettings()


class Config(BaseSettings):

    """Настройки приложения."""

    rabbit_mq: RabbitSettings = RabbitSettings()


config = Config()
