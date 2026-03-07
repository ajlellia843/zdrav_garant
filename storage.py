"""Модуль со стратегией хранения данных — класс PickleStorage."""

import pickle


class PickleStorage:
    """Сериализация и десериализация данных через pickle."""

    @staticmethod
    def save(data, filename: str) -> bool:
        """Сохранить данные в файл.

        Возвращает True при успехе, False при ошибке.
        """
        try:
            with open(filename, "wb") as f:
                pickle.dump(data, f)
            return True
        except (OSError, pickle.PicklingError) as e:
            print(f"  [Ошибка сохранения] {e}")
            return False

    @staticmethod
    def load(filename: str):
        """Загрузить данные из файла.

        Возвращает объект при успехе, None при ошибке.
        """
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            print(f"  [Ошибка] Файл '{filename}' не найден.")
            return None
        except (OSError, pickle.UnpicklingError) as e:
            print(f"  [Ошибка загрузки] {e}")
            return None
