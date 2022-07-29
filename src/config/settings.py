from pydantic import BaseSettings

from security.vault_app_config import vault


class RabbitSettings(BaseSettings):
    host: str = vault.get_secret('rabbit_host')
    port: int = vault.get_secret('rabbit_port')


class Config(BaseSettings):
    rabbit_mq: RabbitSettings = RabbitSettings()


config = Config()
