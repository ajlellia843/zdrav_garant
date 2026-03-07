"""Модуль с классом Patient — наследник Person."""

from person import Person


class Patient(Person):
    """Пациент медицинской системы."""

    def __init__(self, person_id: int, full_name: str, age: int, password: str):
        super().__init__(person_id, full_name, age)
        self.password = password
        self.appointments: list = []

    def edit(self, full_name: str = None, age: int = None, password: str = None):
        """Редактирование данных пациента (имя, возраст, пароль)."""
        super().edit(full_name, age)
        if password is not None:
            self.password = password

    def __str__(self) -> str:
        return f"[Пациент ID: {self.id}] {self.full_name}, возраст: {self.age}"
