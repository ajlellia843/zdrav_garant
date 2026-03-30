"""Общие пути к данным «ЗдравГарант» для консоли и веба."""

import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DEFAULT_SAVE_PATH = os.path.join(DATA_DIR, "zdrav_garant.pkl")


def ensure_data_dir() -> None:
    """Создаёт каталог для файла сохранения, если его ещё нет."""
    os.makedirs(DATA_DIR, exist_ok=True)


def manual_backup_path(raw_name: str, raw_ext: str) -> str:
    """Путь к ручному snapshot в корне проекта (не в data/).

    Пустое имя → zdrav_garant, пустое расширение → pkl.
    Расширение нормализуется (ведущая точка убирается).
    """
    name = raw_name.strip() if raw_name and raw_name.strip() else "zdrav_garant"
    ext_part = raw_ext.strip() if raw_ext and raw_ext.strip() else "pkl"
    ext = ext_part.lstrip(".")
    return os.path.join(PROJECT_ROOT, f"{name}.{ext}")
