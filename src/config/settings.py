from pydantic import BaseSettings, SecretStr

from security.vault_app_config import vault


class RabbitSettings(BaseSettings):
    host: str = vault.get_secret('rabbit_host')
    port: int = vault.get_secret('rabbit_port')
    login: SecretStr = vault.get_secret('rabbit_login')
    password: SecretStr = vault.get_secret('rabbit_password')


class Config(BaseSettings):
    rabbit_mq: RabbitSettings = RabbitSettings()


config = Config()
