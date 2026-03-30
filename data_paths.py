"""Общие пути к данным «ЗдравГарант» для консоли и веба."""

import os

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(_PROJECT_ROOT, "data")
DEFAULT_SAVE_PATH = os.path.join(DATA_DIR, "zdrav_garant.pkl")


def ensure_data_dir() -> None:
    """Создаёт каталог для файла сохранения, если его ещё нет."""
    os.makedirs(DATA_DIR, exist_ok=True)