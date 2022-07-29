"""Модуль содержит конфиг для работы с Vault."""
from pydantic import BaseSettings, SecretStr, AnyUrl


class EnvConfig(BaseSettings):

    """
    Класс начальных настроек приложения.
    Сначала проверит переменные окружения, затем .env файл.
    """

    vault_app_name: str
    vault_url: AnyUrl
    vault_access_token: SecretStr

    class Config:

        """
        Настройки pydantic.
        Подробнее см.
        https://pydantic-docs.helpmanual.io/usage/model_config/
        """

        env_file = '.env'
        env_file_encoding = 'utf-8'


env = EnvConfig()
