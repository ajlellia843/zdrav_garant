"""Модуль со стратегией ввода/вывода — класс ConsoleIO."""


class ConsoleIO:
    """Инкапсулирует весь консольный ввод и вывод приложения."""

    @staticmethod
    def input_str(prompt: str) -> str:
        """Запрос строки у пользователя."""
        return input(prompt)

    @staticmethod
    def input_int(prompt: str) -> int:
        """Запрос целого числа с повторным запросом при ошибке."""
        while True:
            raw = input(prompt)
            try:
                return int(raw)
            except ValueError:
                print(f"  Ошибка: '{raw}' — введите целое число.")

    @staticmethod
    def display(obj) -> None:
        """Вывод одного объекта (через его __str__)."""
        print(obj)

    @staticmethod
    def display_list(items: list, header: str = "") -> None:
        """Вывод списка объектов с необязательным заголовком."""
        if header:
            print(f"\n{'=' * 40}")
            print(f"  {header}")
            print(f"{'=' * 40}")
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
        """Запрос номера пункта меню с проверкой допустимости."""
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
