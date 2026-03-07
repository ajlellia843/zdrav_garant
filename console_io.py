"""Модуль со стратегией ввода/вывода — класс ConsoleIO."""

from datetime import datetime, date

from exceptions import CancelAction

CANCEL_COMMANDS = {"cancel", "q", "quit", "exit"}


class ConsoleIO:
    """Инкапсулирует весь консольный ввод и вывод приложения.

    Все методы ввода поддерживают отмену: если пользователь вводит
    одну из команд (cancel / q / quit / exit), выбрасывается CancelAction.
    """

    # ------------------------------------------------------------------ #
    #  Внутренний ввод с проверкой отмены                                 #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _raw_input(prompt: str) -> str:
        """Считывает строку и проверяет на команду отмены."""
        value = input(prompt)
        if value.strip().lower() in CANCEL_COMMANDS:
            raise CancelAction
        return value

    # ------------------------------------------------------------------ #
    #  Публичные методы ввода                                             #
    # ------------------------------------------------------------------ #
    @staticmethod
    def input_str(prompt: str) -> str:
        """Запрос непустой строки у пользователя.

        Raises:
            CancelAction: при вводе команды отмены.
        """
        while True:
            value = ConsoleIO._raw_input(prompt)
            if value.strip():
                return value.strip()
            print("  Ошибка: значение не может быть пустым.")

    @staticmethod
    def input_int(prompt: str) -> int:
        """Запрос целого числа с повторным запросом при ошибке.

        Raises:
            CancelAction: при вводе команды отмены.
        """
        while True:
            raw = ConsoleIO._raw_input(prompt)
            try:
                return int(raw)
            except ValueError:
                print(f"  Ошибка: '{raw}' — введите целое число.")

    @staticmethod
    def input_positive_int(prompt: str) -> int:
        """Запрос положительного целого числа.

        Raises:
            CancelAction: при вводе команды отмены.
        """
        while True:
            value = ConsoleIO.input_int(prompt)
            if value > 0:
                return value
            print("  Ошибка: число должно быть положительным.")

    @staticmethod
    def input_password(prompt: str, min_length: int = 8) -> str:
        """Запрос пароля с проверкой минимальной длины.

        Raises:
            CancelAction: при вводе команды отмены.
        """
        while True:
            value = ConsoleIO._raw_input(prompt)
            if len(value) >= min_length:
                return value
            print(f"  Ошибка: пароль должен содержать минимум {min_length} символов.")

    @staticmethod
    def input_date(prompt: str) -> str:
        """Запрос даты в формате ДД.ММ.ГГГГ с валидацией.

        Проверяет корректность формата, что дата является реальной
        календарной датой и что она не раньше сегодняшнего дня.

        Raises:
            CancelAction: при вводе команды отмены.
        """
        while True:
            raw = ConsoleIO._raw_input(prompt)
            try:
                parsed = datetime.strptime(raw.strip(), "%d.%m.%Y").date()
            except ValueError:
                print("  Ошибка: неверный формат даты. Используйте ДД.ММ.ГГГГ.")
                continue
            if parsed < date.today():
                print("  Ошибка: дата не может быть раньше сегодняшнего дня.")
                continue
            return raw.strip()

    @staticmethod
    def confirm(prompt: str) -> bool:
        """Запрос подтверждения (да/нет).

        Raises:
            CancelAction: при вводе команды отмены.
        """
        while True:
            raw = ConsoleIO._raw_input(prompt + " (да/нет): ")
            answer = raw.strip().lower()
            if answer in ("да", "д", "yes", "y"):
                return True
            if answer in ("нет", "н", "no", "n"):
                return False
            print("  Ошибка: введите 'да' или 'нет'.")

    # ------------------------------------------------------------------ #
    #  Методы вывода                                                      #
    # ------------------------------------------------------------------ #
    @staticmethod
    def display(obj) -> None:
        """Вывод одного объекта (через его __str__)."""
        print(obj)

    @staticmethod
    def display_list(items: list, header: str = "") -> None:
        """Вывод списка объектов с необязательным заголовком."""
        if header:
            print(f"\n{'=' * 50}")
            print(f"  {header}")
            print(f"{'=' * 50}")
        if not items:
            print("  (список пуст)")
            return
        for item in items:
            print(f"  {item}")

    @staticmethod
    def show_menu(options: dict) -> None:
        """Вывод пунктов меню из словаря {номер: (описание, функция)}."""
        print("\n--- Меню ---")
        for key, (description, _) in options.items():
            print(f"  {key}. {description}")

    @staticmethod
    def input_choice(options: dict) -> int:
        """Запрос номера пункта меню с проверкой допустимости.

        Не выбрасывает CancelAction — меню не отменяется.
        """
        while True:
            raw = input("Выберите пункт: ")
            try:
                choice = int(raw)
                if choice in options:
                    return choice
                print(f"  Нет пункта '{choice}'. Попробуйте снова.")
            except ValueError:
                print(f"  Ошибка: '{raw}' — введите номер пункта.")

    @staticmethod
    def message(text: str) -> None:
        """Вывод информационного сообщения."""
        print(text)

    @staticmethod
    def error(text: str) -> None:
        """Вывод сообщения об ошибке."""
        print(f"  [Ошибка] {text}")

    @staticmethod
    def success(text: str) -> None:
        """Вывод сообщения об успехе."""
        print(f"  [OK] {text}")
