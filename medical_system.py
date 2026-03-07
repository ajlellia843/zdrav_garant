"""Модуль с контейнерным классом MedicalSystem."""

from patient import Patient
from doctor import Doctor
from clinic import Clinic
from appointment import Appointment
from console_io import ConsoleIO
from storage import PickleStorage


class MedicalSystem:
    """Контейнер, хранящий все данные медицинской системы.

    Содержит списки пациентов, врачей, клиник и записей,
    а также методы для работы с ними.
    """

    SAVE_FILE = "zdrav_garant.pkl"

    def __init__(self):
        self.patients: list[Patient] = []
        self.doctors: list[Doctor] = []
        self.clinics: list[Clinic] = []
        self.appointments: list[Appointment] = []
        self.io = ConsoleIO()
        self.storage = PickleStorage()
        self._init_demo_data()

    # ------------------------------------------------------------------ #
    #  Предустановленные демо-данные                                     #
    # ------------------------------------------------------------------ #
    def _init_demo_data(self):
        """Заполняет систему предустановленными клиниками и врачами."""
        self.clinics = [
            Clinic(1, "ЗдравГарант Центральная", "Терапия"),
            Clinic(2, "ЗдравГарант Северная", "Хирургия"),
            Clinic(3, "ЗдравГарант Южная", "Кардиология"),
        ]
        self.doctors = [
            Doctor(1, "Иванов Алексей Петрович", 45, "Терапевт", 1),
            Doctor(2, "Смирнова Елена Викторовна", 38, "Хирург", 2),
            Doctor(3, "Козлов Дмитрий Сергеевич", 50, "Кардиолог", 3),
            Doctor(4, "Новикова Ольга Игоревна", 42, "Терапевт", 1),
            Doctor(5, "Морозов Андрей Николаевич", 55, "Кардиолог", 3),
        ]

    # ------------------------------------------------------------------ #
    #  Поиск                                                              #
    # ------------------------------------------------------------------ #
    def find_patient_by_id(self, patient_id: int) -> Patient | None:
        """Поиск пациента по ID."""
        for p in self.patients:
            if p.id == patient_id:
                return p
        return None

    def _find_doctor_by_id(self, doctor_id: int) -> Doctor | None:
        for d in self.doctors:
            if d.id == doctor_id:
                return d
        return None

    def _find_clinic_by_id(self, clinic_id: int) -> Clinic | None:
        for c in self.clinics:
            if c.clinic_id == clinic_id:
                return c
        return None

    def _next_appointment_id(self) -> int:
        if not self.appointments:
            return 1
        return max(a.appointment_id for a in self.appointments) + 1

    # ------------------------------------------------------------------ #
    #  Регистрация и вход                                                 #
    # ------------------------------------------------------------------ #
    def add_patient(self) -> Patient | None:
        """Регистрация нового пациента через консоль."""
        self.io.message("\n--- Регистрация пациента ---")
        pid = self.io.input_int("  Введите ID: ")
        if self.find_patient_by_id(pid):
            self.io.error("Пациент с таким ID уже существует.")
            return None
        name = self.io.input_str("  Введите ФИО: ")
        age = self.io.input_int("  Введите возраст: ")
        password = self.io.input_str("  Введите пароль: ")
        patient = Patient(pid, name, age, password)
        self.patients.append(patient)
        self.io.success(f"Пациент '{name}' зарегистрирован.")
        return patient

    def login(self) -> Patient | None:
        """Вход пациента в систему."""
        self.io.message("\n--- Вход в систему ---")
        pid = self.io.input_int("  Введите ID: ")
        password = self.io.input_str("  Введите пароль: ")
        patient = self.find_patient_by_id(pid)
        if patient and patient.password == password:
            self.io.success(f"Добро пожаловать, {patient.full_name}!")
            return patient
        self.io.error("Неверный ID или пароль.")
        return None

    # ------------------------------------------------------------------ #
    #  Просмотр данных                                                    #
    # ------------------------------------------------------------------ #
    def show_clinics(self):
        """Вывод списка клиник."""
        self.io.display_list(self.clinics, "Список клиник")

    def show_doctors(self, clinic_id: int = None):
        """Вывод списка врачей (с фильтром по клинике)."""
        if clinic_id is not None:
            filtered = [d for d in self.doctors if d.clinic_id == clinic_id]
        else:
            filtered = self.doctors
        self.io.display_list(filtered, "Список врачей")

    def show_patient_history(self, patient: Patient):
        """Вывод истории записей пациента."""
        records = [a for a in self.appointments if a.patient_id == patient.id]
        self.io.display_list(records, f"История записей — {patient.full_name}")

    # ------------------------------------------------------------------ #
    #  Запись на диагностику                                              #
    # ------------------------------------------------------------------ #
    def add_appointment(self, patient: Patient):
        """Создание новой записи на диагностику."""
        self.io.message("\n--- Запись на диагностику ---")

        self.show_clinics()
        clinic_id = self.io.input_int("  Введите ID клиники: ")
        clinic = self._find_clinic_by_id(clinic_id)
        if not clinic:
            self.io.error("Клиника не найдена.")
            return

        self.show_doctors(clinic_id)
        doctor_id = self.io.input_int("  Введите ID врача: ")
        doctor = self._find_doctor_by_id(doctor_id)
        if not doctor or doctor.clinic_id != clinic_id:
            self.io.error("Врач не найден в выбранной клинике.")
            return

        date = self.io.input_str("  Введите дату (ДД.ММ.ГГГГ): ")

        appt = Appointment(
            self._next_appointment_id(),
            patient.id,
            doctor.id,
            clinic.clinic_id,
            date,
        )
        self.appointments.append(appt)
        patient.appointments.append(appt.appointment_id)
        self.io.success(
            f"Запись #{appt.appointment_id} создана: "
            f"{doctor.full_name}, {clinic.clinic_name}, {date}"
        )

    # ------------------------------------------------------------------ #
    #  Управление записями                                                #
    # ------------------------------------------------------------------ #
    def cancel_appointment(self, patient: Patient):
        """Отмена записи пациента."""
        self.show_patient_history(patient)
        aid = self.io.input_int("  Введите номер записи для отмены: ")
        for appt in self.appointments:
            if appt.appointment_id == aid and appt.patient_id == patient.id:
                if appt.status == "cancelled":
                    self.io.error("Запись уже отменена.")
                    return
                appt.status = "cancelled"
                self.io.success(f"Запись #{aid} отменена.")
                return
        self.io.error("Запись не найдена.")

    def reschedule_appointment(self, patient: Patient):
        """Перенос записи пациента на другую дату."""
        self.show_patient_history(patient)
        aid = self.io.input_int("  Введите номер записи для переноса: ")
        for appt in self.appointments:
            if appt.appointment_id == aid and appt.patient_id == patient.id:
                if appt.status != "scheduled":
                    self.io.error("Можно перенести только запланированную запись.")
                    return
                new_date = self.io.input_str("  Введите новую дату (ДД.ММ.ГГГГ): ")
                appt.date = new_date
                self.io.success(f"Запись #{aid} перенесена на {new_date}.")
                return
        self.io.error("Запись не найдена.")

    # ------------------------------------------------------------------ #
    #  Редактирование профиля                                             #
    # ------------------------------------------------------------------ #
    def edit_patient_data(self, patient: Patient):
        """Редактирование данных пациента."""
        self.io.message("\n--- Настройки безопасности ---")
        self.io.message(f"  Текущие данные: {patient}")

        new_name = self.io.input_str(
            f"  Новое ФИО (Enter — оставить '{patient.full_name}'): "
        )
        new_age_str = self.io.input_str(
            f"  Новый возраст (Enter — оставить {patient.age}): "
        )
        new_password = self.io.input_str(
            "  Новый пароль (Enter — оставить прежний): "
        )

        new_age = None
        if new_age_str:
            try:
                new_age = int(new_age_str)
            except ValueError:
                self.io.error("Некорректный возраст, значение не изменено.")

        patient.edit(
            full_name=new_name if new_name else None,
            age=new_age,
            password=new_password if new_password else None,
        )
        self.io.success("Данные обновлены.")
        self.io.display(patient)

    # ------------------------------------------------------------------ #
    #  Очистка данных                                                     #
    # ------------------------------------------------------------------ #
    def clear_data(self):
        """Полная очистка данных системы и повторное заполнение демо-данными."""
        self.patients.clear()
        self.appointments.clear()
        self._init_demo_data()
        self.io.success("Данные системы очищены.")

    # ------------------------------------------------------------------ #
    #  Сохранение / загрузка                                              #
    # ------------------------------------------------------------------ #
    def save_data(self):
        """Сохранение состояния системы в файл."""
        data = {
            "patients": self.patients,
            "doctors": self.doctors,
            "clinics": self.clinics,
            "appointments": self.appointments,
        }
        if self.storage.save(data, self.SAVE_FILE):
            self.io.success(f"Данные сохранены в '{self.SAVE_FILE}'.")

    def load_data(self):
        """Загрузка состояния системы из файла."""
        data = self.storage.load(self.SAVE_FILE)
        if data is not None:
            self.patients = data.get("patients", [])
            self.doctors = data.get("doctors", [])
            self.clinics = data.get("clinics", [])
            self.appointments = data.get("appointments", [])
            self.io.success(f"Данные загружены из '{self.SAVE_FILE}'.")
