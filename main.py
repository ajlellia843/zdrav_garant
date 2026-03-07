"""Точка входа консольного приложения «ЗдравГарант».

Реализует многоуровневое текстовое меню через словари функций.
"""

from medical_system import MedicalSystem
from console_io import ConsoleIO


def main():
    """Главная функция приложения."""
    system = MedicalSystem()
    io = ConsoleIO()
    current_patient = None

    io.message("=" * 50)
    io.message("  Медицинская система «ЗдравГарант»")
    io.message("=" * 50)

    # ------------------------------------------------------------------ #
    #  Подменю «Настройки безопасности»                                   #
    # ------------------------------------------------------------------ #
    def security_change_name():
        system.edit_patient_name(current_patient)

    def security_change_age():
        system.edit_patient_age(current_patient)

    def security_change_password():
        system.change_password(current_patient)

    def run_security_menu():
        """Цикл подменю настроек безопасности."""
        back = False

        def go_back():
            nonlocal back
            back = True

        security_menu = {
            1: ("Изменить ФИО", security_change_name),
            2: ("Изменить возраст", security_change_age),
            3: ("Изменить пароль", security_change_password),
            4: ("Назад", go_back),
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

    def panel_save():
        system.save_to_file()

    def panel_load():
        system.load_from_file()

    def panel_logout():
        nonlocal current_patient
        current_patient = None
        io.success("Вы вышли из системы.")

    def panel_exit_program():
        io.message("\nСпасибо за использование системы «ЗдравГарант». До свидания!")
        raise SystemExit

    def run_patient_panel():
        """Цикл панели пациента."""
        panel_menu = {
            1: ("Записаться на диагностику", panel_make_appointment),
            2: ("История записей", panel_show_history),
            3: ("Настройки безопасности", panel_security),
            4: ("Сохранить данные в файл", panel_save),
            5: ("Загрузить данные из файла", panel_load),
            6: ("Выйти из аккаунта", panel_logout),
            7: ("Завершить программу", panel_exit_program),
        }
        while current_patient is not None:
            io.message(f"\n  Вы вошли как: {current_patient.full_name}")
            io.show_menu(panel_menu)
            choice = io.input_choice(panel_menu)
            panel_menu[choice][1]()

    # ------------------------------------------------------------------ #
    #  Главное меню (до входа)                                            #
    # ------------------------------------------------------------------ #
    def action_register():
        system.register_patient()

    def action_login():
        nonlocal current_patient
        patient = system.login()
        if patient:
            current_patient = patient
            run_patient_panel()

    def action_exit():
        io.message("\nСпасибо за использование системы «ЗдравГарант». До свидания!")
        raise SystemExit

    main_menu = {
        1: ("Регистрация", action_register),
        2: ("Вход", action_login),
        3: ("Выход", action_exit),
    }

    while True:
        io.show_menu(main_menu)
        choice = io.input_choice(main_menu)
        main_menu[choice][1]()


if __name__ == "__main__":
    main()
