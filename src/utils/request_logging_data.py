"""Модуль содержит функцию для получения заголовков запроса из списка хэдеров сырого запроса."""
from typing import List

from notifier_api.models.access_log import LogData


async def get_logging_data(headers: List[tuple]) -> LogData:
    """
    Функция парсит заголовки.
    x-request-log-message
    x-request-logger-name
    из списка хэдеров сырого запроса
    для логирования ошибок валидации

    Args:
        headers: список хэдеров

    Returns:
        Вернёт pydantic модель cо значениями заголовков.
    """
    log = LogData()
    for header in headers:
        if header[0] == b'x-request-log-message':
            log.message = header[1].decode()
        elif header[0] == b'x-request-logger-name':
            log.logger_name = header[1].decode()
    return log
