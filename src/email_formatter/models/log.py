"""Модуль содержит содержимое для логгеров в виде pydantic моделей."""
from notifier_api.models.base_orjson import BaseOrjson  # type: ignore


class LogError(BaseOrjson):

    """Критические ошибки."""

    failed_get: str = 'Failed get %s from %s'
    drop_message: str = 'Dropped message because %s. X-Request-Id %s'


class LogInfo(BaseOrjson):

    """Уведомления."""

    success_get: str = 'Successful get %s from %s'
    accepted: str = 'Accepted for processing %s'
    success_completed: str = 'Success completed processing %s. X-Request-Id %s'
    started: str = 'Started %s'


class LogWarning(BaseOrjson):

    """Предостережения."""

    retrying: str = 'Retrying message %s due to %s. X-Request-Id %s'


class LogNames(BaseOrjson):

    """Все существующие названия вместе."""

    error: LogError = LogError()
    warn: LogWarning = LogWarning()
    info: LogInfo = LogInfo()


log_names = LogNames()
