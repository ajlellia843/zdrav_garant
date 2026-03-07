"""Модуль с классом Clinic."""


class Clinic:
    """Клиника в медицинской системе."""

    def __init__(self, clinic_id: int, clinic_name: str, department: str):
        self.clinic_id = clinic_id
        self.clinic_name = clinic_name
        self.department = department

    def __str__(self) -> str:
        return (f"[Клиника ID: {self.clinic_id}] {self.clinic_name}, "
                f"отделение: {self.department}")
