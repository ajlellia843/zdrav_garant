"""Модуль с классом Appointment."""


class Appointment:
    """Запись на диагностику."""

    STATUSES = ("scheduled", "cancelled", "completed")

    def __init__(self, appointment_id: int, patient_id: int, doctor_id: int,
                 clinic_id: int, date: str, status: str = "scheduled"):
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.clinic_id = clinic_id
        self.date = date
        self.status = status if status in self.STATUSES else "scheduled"

    def __str__(self) -> str:
        status_ru = {
            "scheduled": "Запланировано",
            "cancelled": "Отменено",
            "completed": "Завершено",
        }
        return (f"[Запись #{self.appointment_id}] Пациент: {self.patient_id}, "
                f"Врач: {self.doctor_id}, Клиника: {self.clinic_id}, "
                f"Дата: {self.date}, Статус: {status_ru.get(self.status, self.status)}")
