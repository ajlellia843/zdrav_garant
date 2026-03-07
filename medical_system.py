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
            Doctor(1, "Иванов", "Иван", "Иванович", 52, "Кардиолог", 1),
            Doctor(2, "Петров", "Петр", "Петрович", 45, "Терапевт", 1),
            Doctor(3, "Сидорова", "Анна", "Сергеевна", 38, "Невролог", 2),
            Doctor(4, "Кузнецов", "Олег", "Викторович", 47, "Хирург", 2),
            Doctor(5, "Пенкин", "Алексей", "Леонидович", 41, "Нарколог", 3),
            Doctor(6, "Васильев", "Игорь", "Николаевич", 50, "Хирург", 3),
        ]

    # ------------------------------------------------------------------ #
    #  Генерация ID пациента                                              #
    # ------------------------------------------------------------------ #
    def _next_patient_id(self) -> str:
        """Генерирует следующий ID пациента в формате PG-XXXXX."""
        max_num = 0
        for p in self.patients:
            pid = str(p.id)
            if pid.startswith("PG-"):
                try:
                    num = int(pid[3:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        return f"PG-{max_num + 1:05d}"

    # ------------------------------------------------------------------ #
    #  Поиск                                                              #
    # ------------------------------------------------------------------ #
    def find_patient_by_id(self, patient_id: str) -> Patient | None:
        """Поиск пациента по строковому ID."""
        for p in self.patients:
            if str(p.id) == patient_id:
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
    #  Ввод пароля с подтверждением (общая логика)                        #
    # ------------------------------------------------------------------ #
    def _input_password_with_confirm(self) -> str:
        """Запрашивает новый пароль и подтверждение.

        При несовпадении возвращает пользователя на шаг ввода нового пароля.
        Raises CancelAction при отмене.
        """
        while True:
            new_pwd = self.io.input_validated_password(
                "  Введите пароль (мин. 8 символов, A-Z, a-z, 0-9, спецсимвол): "
            )
            confirm = self.io._raw_input("  Повторите пароль: ")
            if new_pwd == confirm:
                return new_pwd
            self.io.error("Пароли не совпадают. Введите пароль заново.")

    # ------------------------------------------------------------------ #
    #  Подтверждение личности паролем                                     #
    # ------------------------------------------------------------------ #
    def _verify_password(self, patient: Patient) -> bool:
        """Запрашивает текущий пароль и проверяет его.

        Returns:
            True если пароль верный, False если нет.
        Raises CancelAction при отмене.
        """
        current = self.io._raw_input("  Введите текущий пароль для подтверждения: ")
        if current != patient.password:
            self.io.error("Неверный пароль. Изменение отклонено.")
            return False
        return True

    # ------------------------------------------------------------------ #
    #  Регистрация и вход                                                 #
    # ------------------------------------------------------------------ #
    def register_patient(self) -> Patient | None:
        """Регистрация нового пациента.

        ID генерируется автоматически в формате PG-XXXXX.
        Запрашивает фамилию, имя, отчество, возраст, пароль с подтверждением.
        """
        self.io.message("\n--- Регистрация пациента ---")
        self.io.message("  (для отмены введите cancel)")
        try:
            last_name = self.io.input_str("  Фамилия: ")
            first_name = self.io.input_str("  Имя: ")
            middle_name = self.io.input_optional_str("  Отчество (Enter — пропустить): ")
            age = self.io.input_positive_int("  Возраст: ")

            password = self._input_password_with_confirm()

            pid = self._next_patient_id()
            patient = Patient(pid, last_name, first_name, age, password, middle_name)
            self.patients.append(patient)

            self.io.success(f"Пациент '{patient.full_name}' зарегистрирован.")
            self.io.message(f"  Ваш ID: {pid}")
            self.io.message("  Запомните его для входа в систему.")
            return patient

        except CancelAction:
            self.io.message("  Регистрация отменена.")
            return None

    def login(self) -> Patient | None:
        """Вход пациента в систему.

        Запрашивает строковый ID и пароль.
        """
        self.io.message("\n--- Вход в систему ---")
        self.io.message("  (для отмены введите cancel)")
        try:
            pid = self.io.input_str("  Введите ID (например, PG-00001): ")
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
        """Создание новой записи на диагностику."""
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
    def edit_patient_last_name(self, patient: Patient):
        """Изменение фамилии пациента (с подтверждением паролем)."""
        self.io.message(f"\n  Текущая фамилия: {patient.last_name}")
        try:
            new_val = self.io.input_str("  Введите новую фамилию: ")
            if not self._verify_password(patient):
                return
            patient.edit(last_name=new_val)
            self.io.success(f"Фамилия изменена на '{patient.last_name}'.")
        except CancelAction:
            self.io.message("  Изменение отменено.")

    def edit_patient_first_name(self, patient: Patient):
        """Изменение имени пациента (с подтверждением паролем)."""
        self.io.message(f"\n  Текущее имя: {patient.first_name}")
        try:
            new_val = self.io.input_str("  Введите новое имя: ")
            if not self._verify_password(patient):
                return
            patient.edit(first_name=new_val)
            self.io.success(f"Имя изменено на '{patient.first_name}'.")
        except CancelAction:
            self.io.message("  Изменение отменено.")

    def edit_patient_middle_name(self, patient: Patient):
        """Изменение отчества пациента (с подтверждением паролем)."""
        current = patient.middle_name if patient.middle_name else "(не указано)"
        self.io.message(f"\n  Текущее отчество: {current}")
        try:
            new_val = self.io.input_optional_str("  Введите новое отчество (Enter — убрать): ")
            if not self._verify_password(patient):
                return
            patient.edit(middle_name=new_val)
            self.io.success("Отчество обновлено.")
        except CancelAction:
            self.io.message("  Изменение отменено.")

    def edit_patient_age(self, patient: Patient):
        """Изменение возраста пациента (с подтверждением паролем)."""
        self.io.message(f"\n  Текущий возраст: {patient.age}")
        try:
            new_age = self.io.input_positive_int("  Введите новый возраст: ")
            if not self._verify_password(patient):
                return
            patient.edit(age=new_age)
            self.io.success(f"Возраст изменён на {patient.age}.")
        except CancelAction:
            self.io.message("  Изменение отменено.")

    def change_password(self, patient: Patient):
        """Смена пароля пациента.

        Требует ввод текущего пароля, затем новый пароль с валидацией
        сложности и подтверждением. При несовпадении повтора —
        возврат на ввод нового пароля.
        """
        self.io.message("\n--- Смена пароля ---")
        self.io.message("  (для отмены введите cancel)")
        try:
            current = self.io._raw_input("  Введите текущий пароль: ")
            if current != patient.password:
                self.io.error("Неверный текущий пароль.")
                return

            new_pwd = self._input_password_with_confirm()
            patient.edit(password=new_pwd)
            self.io.success("Пароль успешно изменён.")

        except CancelAction:
            self.io.message("  Смена пароля отменена.")

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
    #  Сохранение / загрузка (остаются для архитектуры лабораторной)       #
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
        """Загрузка состояния системы из файла."""
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
            Doctor(1, "Иванов", "Иван", "Иванович", 52, "Кардиолог", 1),
            Doctor(2, "Петров", "Петр", "Петрович", 45, "Терапевт", 1),
            Doctor(3, "Сидорова", "Анна", "Сергеевна", 38, "Невролог", 2),
            Doctor(4, "Кузнецов", "Олег", "Викторович", 47, "Хирург", 2),
            Doctor(5, "Пенкин", "Алексей", "Леонидович", 41, "Нарколог", 3),
            Doctor(6, "Васильев", "Игорь", "Николаевич", 50, "Хирург", 3),
        ]

        existing_clinic_ids = {c.clinic_id for c in self.clinics}
        for c in demo_clinics:
            if c.clinic_id not in existing_clinic_ids:
                self.clinics.append(c)

        existing_doctor_ids = {d.id for d in self.doctors}
        for d in demo_doctors:
            if d.id not in existing_doctor_ids:
                self.doctors.append(d)
