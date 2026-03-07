"""Модуль со стратегией хранения данных — класс PickleStorage."""

import pickle


class PickleStorage:
    """Сериализация и десериализация данных через pickle.

    Не содержит вызовов print/input — все сообщения
    возвращаются вызывающему коду через возвращаемые значения.
    """

    @staticmethod
    def save(data, filename: str) -> tuple[bool, str]:
        """Сохранить данные в файл.

        Returns:
            Кортеж (успех: bool, сообщение: str).
        """
        try:
            with open(filename, "wb") as f:
                pickle.dump(data, f)
            return True, f"Данные сохранены в '{filename}'."
        except (OSError, pickle.PicklingError) as e:
            return False, f"Ошибка сохранения: {e}"

    @staticmethod
    def load(filename: str) -> tuple[object | None, str]:
        """Загрузить данные из файла.

        Returns:
            Кортеж (данные или None, сообщение: str).
        """
        try:
            with open(filename, "rb") as f:
                data = pickle.load(f)
            return data, f"Данные загружены из '{filename}'."
        except FileNotFoundError:
            return None, f"Файл '{filename}' не найден."
        except (OSError, pickle.UnpicklingError) as e:
            return None, f"Ошибка загрузки: {e}"
