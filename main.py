"""Точка входа консольного приложения 'ЗдравГарант'.

Реализует двухуровневое текстовое меню через словари функций.
"""

from medical_system import MedicalSystem
from console_io import ConsoleIO


def main():
    """Главная функция приложения."""
    system = MedicalSystem()
    io = ConsoleIO()
    current_patient = None

    io.message("=" * 44)
    io.message("  Медицинская система «ЗдравГарант»")
    io.message("=" * 44)

    # ------------------------------------------------------------------ #
    #  Панель пациента (после входа)                                      #
    # ------------------------------------------------------------------ #
    def panel_make_appointment():
        system.add_appointment(current_patient)

    def panel_show_history():
        system.show_patient_history(current_patient)
        if not any(
            a.patient_id == current_patient.id and a.status == "scheduled"
            for a in system.appointments
        ):
            return
        action_menu = {
            1: ("Отменить запись", lambda: system.cancel_appointment(current_patient)),
            2: ("Перенести запись", lambda: system.reschedule_appointment(current_patient)),
            3: ("Назад", lambda: None),
        }
        io.show_menu(action_menu)
        choice = io.input_choice(action_menu)
        action_menu[choice][1]()

    def panel_edit_profile():
        system.edit_patient_data(current_patient)

    def panel_save():
        system.save_data()

    def panel_load():
        system.load_data()

    def panel_logout():
        nonlocal current_patient
        current_patient = None
        io.success("Вы вышли из системы.")

    def run_patient_panel():
        """Цикл панели пациента."""
        panel_menu = {
            1: ("Записаться на диагностику", panel_make_appointment),
            2: ("Посмотреть историю записей", panel_show_history),
            3: ("Изменить данные профиля", panel_edit_profile),
            4: ("Сохранить данные", panel_save),
            5: ("Загрузить данные", panel_load),
            6: ("Выйти из аккаунта", panel_logout),
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
        system.add_patient()

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
