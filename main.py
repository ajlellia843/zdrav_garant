"""Точка входа консольного приложения «ЗдравГарант».

Реализует многоуровневое текстовое меню через словари функций.
Стартовое меню выполняет роль административной панели.
"""

import json
import os
import time

from medical_system import load_system
from console_io import ConsoleIO
from data_paths import DEFAULT_SAVE_PATH


def main():
    """Главная функция приложения."""
    try:
        system = load_system()
    except RuntimeError as e:
        print(f"Ошибка загрузки данных: {e}")
        return
    io = ConsoleIO()
    current_patient = None

    io.message("=" * 50)
    io.message("  Медицинская система «ЗдравГарант»")
    io.message("=" * 50)

    # ------------------------------------------------------------------ #
    #  Подменю «Настройки безопасности» (внутри панели пациента)          #
    # ------------------------------------------------------------------ #
    def security_change_last_name():
        system.edit_patient_last_name(current_patient)

    def security_change_first_name():
        system.edit_patient_first_name(current_patient)

    def security_change_middle_name():
        system.edit_patient_middle_name(current_patient)

    def security_change_age():
        system.edit_patient_age(current_patient)

    def security_change_email():
        system.edit_patient_email(current_patient)

    def security_change_password():
        system.change_password(current_patient)

    def run_security_menu():
        """Цикл подменю настроек безопасности."""
        back = False

        def go_back():
            nonlocal back
            back = True

        security_menu = {
            1: ("Изменить фамилию", security_change_last_name),
            2: ("Изменить имя", security_change_first_name),
            3: ("Изменить отчество", security_change_middle_name),
            4: ("Изменить возраст", security_change_age),
            5: ("Изменить email", security_change_email),
            6: ("Изменить пароль", security_change_password),
            7: ("Назад", go_back),
        }
        while not back:
            io.message(f"\n--- Настройки безопасности ({current_patient.full_name}) ---")
            io.show_menu(security_menu)
            choice = io.input_choice(security_menu)
            security_menu[choice][1]()

    # ------------------------------------------------------------------ #
    #  Подменю «История записей»                                          #
    # ------------------------------------------------------------------ #
    def run_history_menu():
        """Просмотр истории и действия с записями."""
        system.show_patient_history(current_patient)

        has_records = any(
            a.patient_id == current_patient.id
            for a in system.appointments
        )
        if not has_records:
            return

        back = False

        def go_back():
            nonlocal back
            back = True

        history_actions = {
            1: ("Отменить запись", lambda: system.cancel_appointment(current_patient)),
            2: ("Перенести запись", lambda: system.reschedule_appointment(current_patient)),
            3: ("Назад", go_back),
        }
        while not back:
            io.show_menu(history_actions)
            choice = io.input_choice(history_actions)
            history_actions[choice][1]()
            if choice in (1, 2):
                system.show_patient_history(current_patient)

    # ------------------------------------------------------------------ #
    #  Панель пациента (после входа)                                      #
    # ------------------------------------------------------------------ #
    def panel_make_appointment():
        system.add_appointment(current_patient)

    def panel_show_history():
        run_history_menu()

    def panel_security():
        run_security_menu()

    def panel_logout():
        nonlocal current_patient
        current_patient = None
        io.success("Вы вышли из системы.")

    def run_patient_panel():
        """Цикл панели пациента."""
        panel_menu = {
            1: ("Записаться на диагностику", panel_make_appointment),
            2: ("История записей", panel_show_history),
            3: ("Настройки безопасности", panel_security),
            4: ("Выйти из аккаунта", panel_logout),
        }
        while current_patient is not None:
            io.message(f"\n  Вы вошли как: {current_patient.full_name} ({current_patient.id})")
            io.show_menu(panel_menu)
            choice = io.input_choice(panel_menu)
            panel_menu[choice][1]()

    # ------------------------------------------------------------------ #
    #  Стартовое меню (административная панель)                            #
    # ------------------------------------------------------------------ #
    def action_register():
        system.register_patient()

    def action_login():
        nonlocal current_patient
        patient = system.login()
        if patient:
            current_patient = patient
            run_patient_panel()

    def action_show_all():
        system.show_all_patients()

    def action_admin_edit():
        system.admin_edit_patient()

    def action_delete():
        system.delete_patient()

    def action_save():
        system.save_to_file()

    def action_load():
        system.load_from_file()

    # #region agent log
    def _debug_log(hypothesisId: str, location: str, message: str, data: dict | None = None) -> None:
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug-4d3e32.log")
        payload = {
            "sessionId": "4d3e32",
            "runId": "pre-fix",
            "hypothesisId": hypothesisId,
            "id": f"log_{int(time.time() * 1000)}",
            "timestamp": int(time.time() * 1000),
            "location": location,
            "message": message,
            "data": data or {},
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    # #endregion

    def action_exit():
        io.message("\nСпасибо за использование системы «ЗдравГарант». До свидания!")
        # #region agent log
        _debug_log(
            "H1",
            "main.py:action_exit",
            "Exit selected from menu; system.save_to_file() is NOT called in current behavior.",
            {
                "calling_save_to_file": False,
                "save_path": DEFAULT_SAVE_PATH,
                "save_file_exists": os.path.isfile(DEFAULT_SAVE_PATH),
            },
        )
        # #endregion
        raise SystemExit

    main_menu = {
        1: ("Регистрация пользователя", action_register),
        2: ("Вход как пользователь", action_login),
        3: ("Просмотр всех пользователей", action_show_all),
        4: ("Редактирование пользователя", action_admin_edit),
        5: ("Удаление пользователя", action_delete),
        6: ("Сохранение в файл", action_save),
        7: ("Загрузка из файла", action_load),
        8: ("Завершить программу", action_exit),
    }

    while True:
        io.show_menu(main_menu)
        choice = io.input_choice(main_menu)
        main_menu[choice][1]()


if __name__ == "__main__":
    main()
