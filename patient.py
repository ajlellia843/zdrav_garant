"""Модуль с классом Patient — наследник Person."""

from person import Person


class Patient(Person):
    """Пациент медицинской системы.

    ID пациента — строка формата PG-XXXXX (генерируется автоматически).
    Email — обязательное уникальное поле, альтернативный логин.
    """

    def __init__(self, person_id: str, last_name: str, first_name: str,
                 age: int, password: str, email: str,
                 middle_name: str = ""):
        super().__init__(person_id, last_name, first_name, age, middle_name)
        self.password = password
        self.email = email
        self.appointments: list = []

    def edit(self, last_name: str = None, first_name: str = None,
             middle_name: str = None, age: int = None,
             password: str = None, email: str = None):
        """Редактирование данных пациента."""
        super().edit(last_name, first_name, middle_name, age)
        if password is not None:
            self.password = password
        if email is not None:
            self.email = email

    def __str__(self) -> str:
        return (f"[Пациент {self.id}] {self.full_name}, "
                f"возраст: {self.age}, email: {self.email}")
