# flake8: noqa
"""Модуль содержит асинхронную функцию backoff."""
from asyncio import sleep
from functools import wraps
from typing import Union, Callable, Any

from fastapi import HTTPException

from notifier_api.models.http_responses import http
from utils.custom_exceptions import DataBaseError

logger = None


def timeout_limiter(
        max_timeout: Union[int, float],
        start_sleep_time: Union[int, float] = 0.1,
        factor: Union[int, float] = 2,
        border_sleep_time: Union[int, float] = 10
) -> Callable:
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor)
    до граничного времени ожидания (border_sleep_time).
    Вызывает исключение при достижении лимита таймаута.

    Args:
        start_sleep_time: начальное время повтора
        factor: во сколько раз нужно увеличить время ожидания
        border_sleep_time: граничное время ожидания (максимальное значение)
        max_timeout: предел ожидания ответа

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
        async def inner(*args: tuple, **kwargs: dict) -> Any:

            """
            Возвращаемая декоратором функция.
            При неудачном подключении к базе данных повторяет попытку через start_sleep_time.
            После превышения лимита ожидания вызывает исключение

            Args:
                *args: вся неименованная хрень, нужная для func
                **kwargs: вся именованная хрень, нужная для func

            Raises:
                Если ошибка critical — ждём восстановления сервиса,
                иначе продолжаем работу игнорируя исключение.

            Returns:
                Выполняет func пока она работает,
                если «что-то пошло не так» — повторяет попытку вызвать func через интервал start_sleep_time.
                Соответственно,
                чтобы меньше долбать базу без толку интервал увеличивается с каждым разом,
                пока не достигнет предела (border_sleep_time).
            """

            nonlocal start_sleep_time  # Переменная точно не глобальная, но и не локальная вроде :)
            execution_time = 0

            while True:
                try:
                    return await func(*args, **kwargs)

                except Exception as error:

                    if execution_time < max_timeout:
                        await sleep(start_sleep_time)
                        execution_time += start_sleep_time
                        start_sleep_time = min(start_sleep_time * factor, border_sleep_time)
                    else:
                        raise DataBaseError(
                            db_name=func.__name__,
                            message='Database connection timeout',
                            error_type=str(error),
                            critical=True
                        )
        return inner
    return func_wrapper
