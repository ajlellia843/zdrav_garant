"""Модуль с контейнерным классом MedicalSystem."""

from patient import Patient
from doctor import Doctor
from clinic import Clinic
from appointment import Appointment
from console_io import ConsoleIO
from storage import PickleStorage
from exceptions import CancelAction


class MedicalSystem:
    """Контейнер, хранящий все данные медицинской системы.

    Содержит списки пациентов, врачей, клиник и записей,
    а также методы для работы с ними.
    Клиники и врачи соответствуют дизайну проекта «ЗдравГарант».
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
    #  Предустановленные данные из дизайна                                #
    # ------------------------------------------------------------------ #
    def _init_demo_data(self):
        """Заполняет систему клиниками и врачами строго по дизайну."""
        self.clinics = [
            Clinic(1, "Городская клиническая больница №1", "Первичное отделение"),
            Clinic(2, "Центр здоровья «Пульс»", "Первичное отделение"),
            Clinic(3, "Клиника современной медицины", "Первичное отделение"),
        ]
        self.doctors = [
            Doctor(1, "Иванов Иван Иванович", 52, "Кардиолог", 1),
            Doctor(2, "Петров Петр Петрович", 45, "Терапевт", 1),
            Doctor(3, "Сидорова Анна Сергеевна", 38, "Невролог", 2),
            Doctor(4, "Кузнецов Олег Викторович", 47, "Хирург", 2),
            Doctor(5, "Пенкин Алексей Леонидович", 41, "Нарколог", 3),
            Doctor(6, "Васильев Игорь Николаевич", 50, "Хирург", 3),
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
    def register_patient(self) -> Patient | None:
        """Регистрация нового пациента.

        Запрашивает ID, ФИО, возраст, пароль с подтверждением.
        Возвращает созданного пациента или None при отмене.
        """
        self.io.message("\n--- Регистрация пациента ---")
        self.io.message("  (для отмены введите cancel)")
        try:
            pid = self.io.input_positive_int("  Введите ID: ")
            if self.find_patient_by_id(pid):
                self.io.error("Пациент с таким ID уже существует.")
                return None

            name = self.io.input_str("  Введите ФИО: ")
            age = self.io.input_positive_int("  Введите возраст: ")

            while True:
                password = self.io.input_password("  Введите пароль (мин. 8 символов): ")
                password_confirm = self.io.input_password("  Повторите пароль: ")
                if password == password_confirm:
                    break
                self.io.error("Пароли не совпадают. Попробуйте снова.")

            patient = Patient(pid, name, age, password)
            self.patients.append(patient)
            self.io.success(f"Пациент '{name}' зарегистрирован.")
            return patient

        except CancelAction:
            self.io.message("  Регистрация отменена.")
            return None

    def login(self) -> Patient | None:
        """Вход пациента в систему.

        Возвращает объект пациента или None при неудаче/отмене.
        """
        self.io.message("\n--- Вход в систему ---")
        self.io.message("  (для отмены введите cancel)")
        try:
            pid = self.io.input_int("  Введите ID: ")
            password = self.io._raw_input("  Введите пароль: ")

            patient = self.find_patient_by_id(pid)
            if patient and patient.password == password:
                self.io.success(f"Добро пожаловать, {patient.full_name}!")
                return patient

            self.io.error("Неверный ID или пароль.")
            return None

        except CancelAction:
            self.io.message("  Вход отменён.")
            return None

    # ------------------------------------------------------------------ #
    #  Просмотр данных                                                    #
    # ------------------------------------------------------------------ #
    def show_clinics(self):
        """Вывод списка клиник."""
        self.io.display_list(self.clinics, "Список клиник")

    def show_doctors_by_clinic(self, clinic_id: int):
        """Вывод списка врачей конкретной клиники."""
        filtered = [d for d in self.doctors if d.clinic_id == clinic_id]
        self.io.display_list(filtered, "Врачи выбранной клиники")

    def show_patient_history(self, patient: Patient):
        """Вывод истории записей пациента."""
        records = [a for a in self.appointments if a.patient_id == patient.id]
        self.io.display_list(records, f"История записей — {patient.full_name}")

    # ------------------------------------------------------------------ #
    #  Запись на диагностику                                              #
    # ------------------------------------------------------------------ #
    def add_appointment(self, patient: Patient):
        """Создание новой записи на диагностику.

        Пользователь выбирает клинику, врача и дату.
        Операцию можно отменить на любом шаге.
        """
        self.io.message("\n--- Запись на диагностику ---")
        self.io.message("  (для отмены введите cancel)")
        try:
            self.show_clinics()
            clinic_id = self.io.input_int("  Введите ID клиники: ")
            clinic = self._find_clinic_by_id(clinic_id)
            if not clinic:
                self.io.error("Клиника не найдена.")
                return

            self.show_doctors_by_clinic(clinic_id)
            doctor_id = self.io.input_int("  Введите ID врача: ")
            doctor = self._find_doctor_by_id(doctor_id)
            if not doctor or doctor.clinic_id != clinic_id:
                self.io.error("Врач не найден в выбранной клинике.")
                return

            date_str = self.io.input_date("  Введите дату приёма (ДД.ММ.ГГГГ): ")

            appt = Appointment(
                self._next_appointment_id(),
                patient.id,
                doctor.id,
                clinic.clinic_id,
                date_str,
            )
            self.appointments.append(appt)
            patient.appointments.append(appt.appointment_id)
            self.io.success(
                f"Запись #{appt.appointment_id} создана: "
                f"{doctor.full_name}, {clinic.clinic_name}, {date_str}"
            )

        except CancelAction:
            self.io.message("  Запись на диагностику отменена.")

    # ------------------------------------------------------------------ #
    #  Управление записями                                                #
    # ------------------------------------------------------------------ #
    def cancel_appointment(self, patient: Patient):
        """Отмена записи пациента."""
        self.io.message("\n--- Отмена записи ---")
        self.io.message("  (для отмены действия введите cancel)")
        try:
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

        except CancelAction:
            self.io.message("  Действие отменено.")

    def reschedule_appointment(self, patient: Patient):
        """Перенос записи пациента на другую дату."""
        self.io.message("\n--- Перенос записи ---")
        self.io.message("  (для отмены действия введите cancel)")
        try:
            self.show_patient_history(patient)
            aid = self.io.input_int("  Введите номер записи для переноса: ")
            for appt in self.appointments:
                if appt.appointment_id == aid and appt.patient_id == patient.id:
                    if appt.status != "scheduled":
                        self.io.error("Можно перенести только запланированную запись.")
                        return
                    new_date = self.io.input_date("  Введите новую дату (ДД.ММ.ГГГГ): ")
                    appt.date = new_date
                    self.io.success(f"Запись #{aid} перенесена на {new_date}.")
                    return
            self.io.error("Запись не найдена.")

        except CancelAction:
            self.io.message("  Перенос отменён.")

    # ------------------------------------------------------------------ #
    #  Настройки безопасности                                             #
    # ------------------------------------------------------------------ #
    def edit_patient_name(self, patient: Patient):
        """Изменение ФИО пациента."""
        self.io.message(f"\n  Текущее ФИО: {patient.full_name}")
        try:
            new_name = self.io.input_str("  Введите новое ФИО: ")
            patient.edit(full_name=new_name)
            self.io.success(f"ФИО изменено на '{patient.full_name}'.")
        except CancelAction:
            self.io.message("  Изменение ФИО отменено.")

    def edit_patient_age(self, patient: Patient):
        """Изменение возраста пациента."""
        self.io.message(f"\n  Текущий возраст: {patient.age}")
        try:
            new_age = self.io.input_positive_int("  Введите новый возраст: ")
            patient.edit(age=new_age)
            self.io.success(f"Возраст изменён на {patient.age}.")
        except CancelAction:
            self.io.message("  Изменение возраста отменено.")

    def change_password(self, patient: Patient):
        """Смена пароля пациента.

        Требует ввод текущего пароля, затем новый пароль
        с подтверждением и проверкой длины (>= 8 символов).
        """
        self.io.message("\n--- Смена пароля ---")
        self.io.message("  (для отмены введите cancel)")
        try:
            current = self.io._raw_input("  Введите текущий пароль: ")
            if current != patient.password:
                self.io.error("Неверный текущий пароль.")
                return

            while True:
                new_pwd = self.io.input_password("  Введите новый пароль (мин. 8 символов): ")
                confirm = self.io.input_password("  Повторите новый пароль: ")
                if new_pwd == confirm:
                    break
                self.io.error("Пароли не совпадают. Попробуйте снова.")

            patient.edit(password=new_pwd)
            self.io.success("Пароль успешно изменён.")

        except CancelAction:
            self.io.message("  Смена пароля отменена.")

    def edit_patient_data(self, patient: Patient):
        """Устаревший метод — для обратной совместимости вызывает подменю."""
        self.edit_patient_name(patient)

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
    def save_to_file(self):
        """Сохранение состояния системы в файл."""
        data = {
            "patients": self.patients,
            "doctors": self.doctors,
            "clinics": self.clinics,
            "appointments": self.appointments,
        }
        ok, msg = self.storage.save(data, self.SAVE_FILE)
        if ok:
            self.io.success(msg)
        else:
            self.io.error(msg)

    def load_from_file(self):
        """Загрузка состояния системы из файла.

        После загрузки проверяет наличие демо-клиник и врачей,
        чтобы не создавать дубликатов.
        """
        data, msg = self.storage.load(self.SAVE_FILE)
        if data is not None:
            self.patients = data.get("patients", [])
            self.doctors = data.get("doctors", [])
            self.clinics = data.get("clinics", [])
            self.appointments = data.get("appointments", [])
            self._ensure_demo_data()
            self.io.success(msg)
        else:
            self.io.error(msg)

    def _ensure_demo_data(self):
        """Добавляет демо-клиники и врачей, если они отсутствуют после загрузки."""
        demo_clinics = [
            Clinic(1, "Городская клиническая больница №1", "Первичное отделение"),
            Clinic(2, "Центр здоровья «Пульс»", "Первичное отделение"),
            Clinic(3, "Клиника современной медицины", "Первичное отделение"),
        ]
        demo_doctors = [
            Doctor(1, "Иванов Иван Иванович", 52, "Кардиолог", 1),
            Doctor(2, "Петров Петр Петрович", 45, "Терапевт", 1),
            Doctor(3, "Сидорова Анна Сергеевна", 38, "Невролог", 2),
            Doctor(4, "Кузнецов Олег Викторович", 47, "Хирург", 2),
            Doctor(5, "Пенкин Алексей Леонидович", 41, "Нарколог", 3),
            Doctor(6, "Васильев Игорь Николаевич", 50, "Хирург", 3),
        ]

        existing_clinic_ids = {c.clinic_id for c in self.clinics}
        for c in demo_clinics:
            if c.clinic_id not in existing_clinic_ids:
                self.clinics.append(c)

        existing_doctor_ids = {d.id for d in self.doctors}
        for d in demo_doctors:
            if d.id not in existing_doctor_ids:
                self.doctors.append(d)
