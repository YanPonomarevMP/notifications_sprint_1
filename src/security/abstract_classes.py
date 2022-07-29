"""Модуль с абстрактными классами для работы с хранилищем секретов."""
from abc import ABC, abstractmethod
from typing import Tuple


class AbstractAppConfig(ABC):
    """Класс для конфигурирования приложения из хранилища секретов."""

    @abstractmethod
    def get_secret(self, key: str) -> str:  # noqa:WPS463
        """
        Метод достаёт значение ключа из хранилища.

        Args:
            key: ключ

        Returns:
            Возвращает значение в виде строки
        """
        pass


class AbstractDbCredentials(ABC):
    """Класс создаёт одноразовых пользователей для входа в базу данных."""

    @abstractmethod
    def get_temporary_credentials(self) -> Tuple[str, str]:  # noqa:WPS463
        """
        Метод достаёт одноразового пользователя и пароль из хранилища.

        Returns:
            Возвращает значение в виде строки
        """
        pass


class AbstractEncryptor(ABC):
    """Класс шифрует и расшифровывает данные, а также генерирует HMAC от данных."""

    @abstractmethod
    def encrypt_data(self, plaintext: str) -> str:  # noqa:WPS463
        """
        Метод шифрует данные.

        Args:
            plaintext: строка для шифрования

        Returns:
            Возвращает зашифрованные данные в виде строки
        """
        pass

    @abstractmethod
    def decrypt_data(self, ciphertext: str) -> str:  # noqa:WPS463
        """
        Метод расшифровывает данные.

        Args:
            ciphertext: строка для расшифрования

        Returns:
            Возвращает расшифрованные данные в виде строки
        """
        pass

    @abstractmethod
    def hmac_from_data(self, plaintext: str) -> str:  # noqa:WPS463
        """
        Метод рассчитывает хэш от данных.

        Args:
            plaintext: строка для расчёта хэш

        Returns:
            Возвращает хэш в виде строки
        """
        pass
