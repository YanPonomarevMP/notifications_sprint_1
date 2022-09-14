"""Модуль содержит конфигуратор приложения из HashiCorp Vault."""
from logging import getLogger
from typing import Optional

import hvac

from security.abstract_classes import AbstractAppConfig
from security.exceptions_handler import exceptions_handler


class VaultAppConfig(AbstractAppConfig):
    """Класс конфигуратор приложения из хранилища HashiCorp Vault."""

    def __init__(self, vault_client: hvac.Client, app_name: str, dev_mode: bool = False) -> None:
        """
        Конструктор.

        Args:
            vault_client: Клиент для доступа к HashiCorp Vault
            app_name: Имя приложения. Используется в vault как -path=app_name в kv secrets engine
            dev_mode: Режим разработки, в котором используются значения по умолчанию вместо значений из vault
        """
        self.vault = vault_client
        self.app_name = app_name
        self.dev_mode = dev_mode

    @exceptions_handler(__name__)
    def get_setting(self, key: str, dev_mode_value: Optional[str] = None) -> str:
        """
        Метод достаёт значение по ключу key из HashiCorp Vault.

        Args:
            key: ключ, значение которого необходимо достать
            dev_mode_value: значение для использования в dev_mode

        Returns:
            Возвращает значение, соответствующее ключу в виде строки
        """
        if self.dev_mode:
            if dev_mode_value:
                return dev_mode_value

        response = self.vault.secrets.kv.v1.read_secret(path=key, mount_point=self.app_name)
        logger.info('SUCCESSFUL get setting %s', key)
        return response['data']['value']


logger = getLogger(__name__)
