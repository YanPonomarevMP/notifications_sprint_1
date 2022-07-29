"""Модуль содержит клиент для подключения к HashiCorp Vault."""
import hvac

from security.env_config import env

client = hvac.Client(
    url=env.vault_url,
    token=env.vault_access_token.get_secret_value()
)
