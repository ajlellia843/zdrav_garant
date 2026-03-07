"""Модуль с базовым классом Person."""


class Person:
    """Базовый класс, представляющий человека в системе."""

    def __init__(self, person_id: int, full_name: str, age: int):
        self.id = person_id
        self.full_name = full_name
        self.age = age

    def edit(self, full_name: str = None, age: int = None):
        """Редактирование данных персоны."""
        if full_name is not None:
            self.full_name = full_name
        if age is not None:
            self.age = age

    def __str__(self) -> str:
        return f"[ID: {self.id}] {self.full_name}, возраст: {self.age}"
