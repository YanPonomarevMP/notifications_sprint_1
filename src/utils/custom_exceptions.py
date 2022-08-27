"""Модуль содержит кастомные исключения."""

class DataBaseError(Exception):

    """Класс с собственным исключением для работы с кешом и бд."""

    def __init__(
            self,
            db_name: str,
            message: str,
            error_type: str,
            critical: bool = False
    ) -> None:

        """
        Конструктор.

        Args:
            db_name: название базы данных
            message: выводимое сообщение об ошибке
            error_type: само возникшее исключение
            critical: критична ли ошибка, можно ли продолжить программу игнорируя её
        """
        self.db_name = db_name
        self.message = message
        self.error_type = error_type
        self.critical = critical

        super().__init__()

    def __str__(self) -> str:
        """Формат вывода сообщения."""
        return f'{self.db_name} | {self.message} {self.error_type}'
