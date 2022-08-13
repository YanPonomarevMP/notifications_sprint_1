"""Модуль содержит конфигуратор приложения из HashiCorp Vault."""
from logging import getLogger

import hvac

from security.abstract_classes import AbstractAppConfig
from security.env_config import env
from security.vault_client import client
from utils.backoff import backoff


class VaultAppConfig(AbstractAppConfig):
    """Класс конфигуратор приложения из хранилища HashiCorp Vault."""

    def __init__(self, vault_client: hvac.Client, app_name: str) -> None:
        """
        Конструктор.

        Args:
            vault_client: Клиент для доступа к HashiCorp Vault
            app_name: Имя приложения. Используется в vault как -path=app_name в kv secrets engine
        """
        self.vault = vault_client
        self.app_name = app_name

    @backoff()
    def get_secret(self, key: str) -> str:
        """
        Метод достаёт значение по ключу key из HashiCorp Vault.

        Args:
            key: ключ, значение которого необходимо достать

        Returns:
            Возвращает значение, соответствующее ключу в виде строки
        """

        response = self.vault.secrets.kv.v1.read_secret(path=key, mount_point=self.app_name)
        logger.info('SUCCESSFUL get_secret %s', key)
        return response['data']['value']


logger = getLogger(__name__)
vault = VaultAppConfig(vault_client=client, app_name=env.vault_app_name)
