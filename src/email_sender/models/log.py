"""Модуль содержит содержимое для логгеров в виде pydantic моделей."""
from notifier_api.models.base_orjson import BaseOrjson


class LogError(BaseOrjson):

    """Критические ошибки."""

    drop_message: str = 'Dropped message because %s'


class LogInfo(BaseOrjson):

    """Уведомления."""

    success_data_sent: str = 'Success data sent %s'
    started: str = 'Started %s'
    accepted: str = 'Accepted for processing %s'


class LogWarning(BaseOrjson):

    """Предостережения."""

    retrying: str = 'Retrying message %s due to %s'


class LogNames(BaseOrjson):

    """Все существующие названия вместе."""

    error: LogError = LogError()
    warn: LogWarning = LogWarning()
    info: LogInfo = LogInfo()


log_names = LogNames()
