"""Модуль с базовым классом Person."""


class Person:
    """Базовый класс, представляющий человека в системе.

    ФИО хранится раздельно: фамилия, имя, отчество.
    """

    def __init__(self, person_id, last_name: str, first_name: str,
                 age: int, middle_name: str = ""):
        self.id = person_id
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name
        self.age = age

    @property
    def full_name(self) -> str:
        """Полное ФИО без лишних пробелов."""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)

    def edit(self, last_name: str = None, first_name: str = None,
             middle_name: str = None, age: int = None):
        """Редактирование данных персоны."""
        if last_name is not None:
            self.last_name = last_name
        if first_name is not None:
            self.first_name = first_name
        if middle_name is not None:
            self.middle_name = middle_name
        if age is not None:
            self.age = age

    def __str__(self) -> str:
        return f"[ID: {self.id}] {self.full_name}, возраст: {self.age}"
