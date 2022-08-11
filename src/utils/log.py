"""В этом файле функция для создания логгеров."""
import logging
import sys
from typing import TextIO


def create_logger(
    name: str,
    format_line: str = '%(levelname)s | %(asctime)s | %(name)s | %(message)s',
    stream_out: TextIO = sys.stdout,
    level: str = 'INFO'
) -> logging.Logger:

    """
    Функция создаёт логгер.

    Args:
        name: имя модуля, где задействован логгер
        format_line: форматная строка логгера
        stream_out: тип потока, могут быть файл, консоль и т.д.
        level: уровень, с которого начинаем писать лог

    Returns:
        Возвращает полноценный логгер, с настройками, которые объяснены выше.
    """

    logger = logging.getLogger(name)
    formatter = logging.Formatter(format_line)
    handler = logging.StreamHandler(stream=stream_out)  # noqa:WPS110
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
