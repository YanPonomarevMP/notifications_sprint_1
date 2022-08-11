"""Модуль содержит функцию backoff."""
import sys
from functools import wraps
from time import sleep
from typing import Union, Callable, Any

from utils.log import create_logger


def backoff(
    start_sleep_time: Union[int, float] = 0.1,
    factor: Union[int, float] = 2,
    border_sleep_time: Union[int, float] = 10
) -> Callable:
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor)
    до граничного времени ожидания (border_sleep_time).

    Args:
        start_sleep_time: начальное время повтора
        factor: во сколько раз нужно увеличить время ожидания
        border_sleep_time: граничное время ожидания (максимальное значение)

    Returns:
        Пробует выполнить функцию func и, если что-то пошло не так, «засыпает» на какое-то время.
    """

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

            nonlocal start_sleep_time  # Переменная точно не глобальная, но и не локальная вроде :)

            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as error:

                    logger.error('FAILED RUN %s.%s | ERROR %s', func.__module__, func.__name__, error)
                    logger.info('Next try run %s.%s in %s seconds.', func.__module__, func.__name__, start_sleep_time)

                    sleep(start_sleep_time)
                    start_sleep_time = min(start_sleep_time * factor, border_sleep_time)  # noqa: WPS442

        return inner

    return func_wrapper


logger = create_logger(__name__, stream_out=sys.stderr)
