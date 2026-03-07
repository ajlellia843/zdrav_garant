"""Модуль с классом Doctor — наследник Person."""

from person import Person


class Doctor(Person):
    """Врач медицинской системы."""

    def __init__(self, person_id: int, full_name: str, age: int,
                 specialization: str, clinic_id: int):
        super().__init__(person_id, full_name, age)
        self.specialization = specialization
        self.clinic_id = clinic_id

    def __str__(self) -> str:
        return (f"[Врач ID: {self.id}] {self.full_name}, "
                f"специализация: {self.specialization}")
