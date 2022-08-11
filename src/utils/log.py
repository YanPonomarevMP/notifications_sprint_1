"""В этом файле функция для создания логгеров."""
import logging
import sys
from typing import TextIO
from pythonjsonlogger import jsonlogger


def create_logger(
    name: str,
    format_line: str = '%(levelname)s | %(asctime)s | %(name)s | %(message)s',
    stream_out: TextIO = sys.stdout,
    log_file: str = 'log.json',
    level: str = 'INFO'
) -> logging.Logger:

    """
    Функция создаёт логгер.

    Args:
        name: имя модуля, где задействован логгер
        format_line: форматная строка логгера
        stream_out: тип потока, могут быть файл, консоль и т.д.
        log_file: путь и имя файла json
        level: уровень, с которого начинаем писать лог

    Returns:
        Возвращает полноценный логгер, с настройками, которые объяснены выше.
    """

    logger = logging.getLogger(name)

    console_formatter = logging.Formatter(format_line)
    console_handler = logging.StreamHandler(stream=stream_out)  # noqa:WPS110
    console_handler.setFormatter(console_formatter)

    json_formatter = jsonlogger.JsonFormatter(format_line)
    json_handler = logging.FileHandler(filename=log_file)  # noqa:WPS110
    json_handler.setFormatter(json_formatter)

    logger.addHandler(json_handler)
    logger.addHandler(console_handler)
    logger.setLevel(level)
    return logger
