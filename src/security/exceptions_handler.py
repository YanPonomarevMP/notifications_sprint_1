"""Модуль содержит функцию backoff."""
from functools import wraps
from logging import getLogger
from typing import Callable, Any


def exceptions_handler(
    logger_name: str,
) -> Callable:
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor)
    до граничного времени ожидания (border_sleep_time).

    Args:
        logger_name: имя логгера

    Returns:
        Пробует выполнить функцию func и, если что-то пошло не так, «засыпает» на какое-то время.
    """
    logger = getLogger(logger_name)

    def func_wrapper(func: Callable) -> Callable:

        """
        Декоратор функций (в нашем случае для подключения к базе данных).
        Но может обрабатывать любую функцию, где возможны непредвиденные ошибки с подключением.

        Args:
            func: функция, которая подключается к базе

        Returns:
            Возвращает функцию, которая и выполняет алгоритм.
        """

        @wraps(func)
        def inner(*args: tuple, **kwargs: dict) -> Any:

            """
            Возвращаемая декоратором функция.
            При неудачном подключении к базе данных повторяет попытку через start_sleep_time.

            Args:
                args: вся неименованная хрень, нужная для func
                kwargs: вся именованная хрень, нужная для func

            Returns:
                Выполняет func пока она работает,
                если «что-то пошло не так» — повторяет попытку вызвать func через интервал start_sleep_time.
                Соответственно,
                чтобы меньше долбать базу без толку интервал увеличивается с каждым разом,
                пока не достигнет предела (border_sleep_time).
            """
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as error:

                    logger.error('FAILED RUN %s.%s | ERROR %s', func.__module__, func.__name__, error)
                    raise SystemExit('Program stopped')

        return inner

    return func_wrapper
