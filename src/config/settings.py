from pydantic import BaseSettings, SecretStr

from security.vault_app_config import vault


class RabbitSettings(BaseSettings):
    host: str = vault.get_secret('rabbit_host')
    port: int = vault.get_secret('rabbit_port')


class PostgresSettings(BaseSettings):
    login: SecretStr = vault.get_secret('pg_user')  # имя поля user пересекается с переменной окружения user
    password: SecretStr = vault.get_secret('pg_password')
    host: str = vault.get_secret('pg_host')
    db_name: str = vault.get_secret('pg_db_name')


class Config(BaseSettings):
    rabbit_mq: RabbitSettings = RabbitSettings()
    pg: PostgresSettings = PostgresSettings()


config = Config()
