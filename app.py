"""Веб-точка входа приложения «ЗдравГарант» на Flask.

Использует MedicalSystem как сервис данных.
Состояние синхронизируется с консолью через общий файл в data/.
"""

import atexit
import os
import functools
import sys
from datetime import datetime, date

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, abort, jsonify,
)

from medical_system import load_system, save_system_to_path
from patient import Patient
from appointment import Appointment
from validators import validate_password, validate_email
from data_paths import DEFAULT_SAVE_PATH, manual_backup_path

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "zdrav-garant-secret-key")

system = load_system()


def _is_runtime_process() -> bool:
    """True для единственного процесса, который должен писать autosave."""
    if not app.debug:
        return True
    return os.environ.get("WERKZEUG_RUN_MAIN") == "true"


def _autosave_on_exit():
    if not _is_runtime_process():
        return
    try:
        ok, msg = save_system_to_path(system, DEFAULT_SAVE_PATH)
        if not ok:
            print(
                f"Предупреждение: автосохранение при завершении не выполнено: {msg}",
                file=sys.stderr,
            )
    except Exception as exc:  # noqa: BLE001
        print(
            f"Предупреждение: автосохранение при завершении: {exc}",
            file=sys.stderr,
        )


atexit.register(_autosave_on_exit)


# ------------------------------------------------------------------ #
#  Вспомогательные функции                                            #
# ------------------------------------------------------------------ #

def _current_patient():
    """Возвращает текущего пациента из сессии или None."""
    pid = session.get("patient_id")
    if pid:
        return system.find_patient_by_id(pid)
    return None


def login_required(view):
    """Декоратор: перенаправляет неавторизованных на /login."""
    @functools.wraps(view)
    def wrapped(**kwargs):
        if not _current_patient():
            flash("Необходимо войти в систему.", "error")
            return redirect(url_for("login"))
        return view(**kwargs)
    return wrapped


def admin_required(view):
    """Декоратор: только для пользователей с ролью admin."""
    @functools.wraps(view)
    def wrapped(**kwargs):
        patient = _current_patient()
        if not patient:
            flash("Необходимо войти в систему.", "error")
            return redirect(url_for("login"))
        if getattr(patient, "role", "user") != "admin":
            abort(403)
        return view(**kwargs)
    return wrapped


_APPOINTMENT_HIGHLIGHT_KEYS = frozenset({"clinic", "doctor", "date"})


def _parse_appointment_highlight_arg(raw: str) -> list[str]:
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip() in _APPOINTMENT_HIGHLIGHT_KEYS]


def _dashboard_appointment_redirect_params(
    clinic_id: int | None,
    doctor_id: int | None,
    date_str: str,
    highlight: list[str] | None = None,
) -> dict:
    params: dict = {}
    if clinic_id:
        params["clinic_id"] = clinic_id
    if doctor_id:
        params["doctor_id"] = doctor_id
    if date_str:
        params["date"] = date_str
    if highlight:
        filtered = [h for h in highlight if h in _APPOINTMENT_HIGHLIGHT_KEYS]
        if filtered:
            params["highlight"] = ",".join(filtered)
    return params


@app.context_processor
def inject_current_patient():
    """Передаёт текущего пациента во все шаблоны."""
    return {"current_patient": _current_patient()}


# ------------------------------------------------------------------ #
#  Главная страница (лендинг)                                         #
# ------------------------------------------------------------------ #

@app.route("/")
def index():
    patient = _current_patient()
    if patient:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


# ------------------------------------------------------------------ #
#  Аутентификация                                                     #
# ------------------------------------------------------------------ #

@app.route("/login", methods=["GET", "POST"])
def login():
    if _current_patient():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        login_val = request.form.get("login", "").strip()
        password = request.form.get("password", "")

        if not login_val or not password:
            flash("Оба поля должны быть заполнены.", "error")
            return render_template("login.html")

        patient = system.find_patient_by_login(login_val)
        if patient and patient.password == password:
            session["patient_id"] = str(patient.id)
            flash(f"Добро пожаловать, {patient.full_name}!", "success")
            return redirect(url_for("dashboard"))

        flash("Неверный ID/email или пароль.", "error")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if _current_patient():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        last_name = request.form.get("last_name", "").strip()
        first_name = request.form.get("first_name", "").strip()
        middle_name = request.form.get("middle_name", "").strip()
        age_str = request.form.get("age", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        form_data = {
            "last_name": last_name,
            "first_name": first_name,
            "middle_name": middle_name,
            "age": age_str,
            "email": email,
        }

        if not last_name or not first_name or not age_str or not email or not password:
            flash("Все обязательные поля должны быть заполнены.", "error")
            return render_template("register.html", **form_data)

        try:
            age = int(age_str)
            if age <= 0:
                raise ValueError
        except ValueError:
            flash("Возраст должен быть положительным целым числом.", "error")
            return render_template("register.html", **form_data)

        email_ok, email_err = validate_email(email)
        if not email_ok:
            flash(email_err, "error")
            return render_template("register.html", **form_data)

        if not system._is_email_unique(email):
            flash("Этот email уже зарегистрирован.", "error")
            return render_template("register.html", **form_data)

        pwd_ok, pwd_errors = validate_password(password)
        if not pwd_ok:
            flash("Пароль не соответствует требованиям: " + "; ".join(pwd_errors), "error")
            return render_template("register.html", **form_data)

        if password != confirm:
            flash("Пароли не совпадают.", "error")
            return render_template("register.html", **form_data)

        pid = system._next_patient_id()
        patient = Patient(pid, last_name, first_name, age, password, email,
                          middle_name, role="user")
        system.patients.append(patient)

        session["patient_id"] = str(patient.id)
        flash(f"Профиль создан. Ваш ID: {pid}", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("patient_id", None)
    flash("Вы вышли из системы.", "success")
    return redirect(url_for("login"))


# ------------------------------------------------------------------ #
#  Клинический обзор / Запись на диагностику                          #
# ------------------------------------------------------------------ #

@app.route("/dashboard")
@login_required
def dashboard():
    patient = _current_patient()
    selected_clinic_id = request.args.get("clinic_id", type=int)
    saved_doctor_id = request.args.get("doctor_id", type=int)
    saved_date = request.args.get("date", "")

    selected_clinic = None
    doctors = []
    if selected_clinic_id:
        selected_clinic = system._find_clinic_by_id(selected_clinic_id)
        if selected_clinic:
            doctors = [d for d in system.doctors if d.clinic_id == selected_clinic_id]

    highlight_fields = _parse_appointment_highlight_arg(
        request.args.get("highlight", ""),
    )

    return render_template(
        "dashboard.html",
        clinics=system.clinics,
        selected_clinic=selected_clinic,
        doctors=doctors,
        patient=patient,
        saved_doctor_id=saved_doctor_id,
        saved_date=saved_date,
        today=date.today().isoformat(),
        highlight_fields=highlight_fields,
    )


@app.route("/appointment", methods=["POST"])
@login_required
def create_appointment():
    patient = _current_patient()
    clinic_id = request.form.get("clinic_id", type=int)
    doctor_id = request.form.get("doctor_id", type=int)
    date_str = request.form.get("date", "").strip()

    if not clinic_id or not doctor_id or not date_str:
        flash("Все поля обязательны.", "error")
        missing: list[str] = []
        if not clinic_id:
            missing.append("clinic")
        if not doctor_id:
            missing.append("doctor")
        if not date_str:
            missing.append("date")
        return redirect(
            url_for(
                "dashboard",
                **_dashboard_appointment_redirect_params(
                    clinic_id, doctor_id, date_str, missing,
                ),
            ),
        )

    clinic = system._find_clinic_by_id(clinic_id)
    if not clinic:
        flash("Клиника не найдена.", "error")
        return redirect(url_for("dashboard", highlight="clinic"))

    doctor = system._find_doctor_by_id(doctor_id)
    if not doctor or doctor.clinic_id != clinic_id:
        flash("Врач не найден в выбранной клинике.", "error")
        return redirect(
            url_for(
                "dashboard",
                **_dashboard_appointment_redirect_params(
                    clinic_id, doctor_id, date_str, ["doctor"],
                ),
            ),
        )

    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Неверный формат даты.", "error")
        return redirect(
            url_for(
                "dashboard",
                **_dashboard_appointment_redirect_params(
                    clinic_id, doctor_id, date_str, ["date"],
                ),
            ),
        )

    if parsed < date.today():
        flash("Дата не может быть раньше сегодняшнего дня.", "error")
        return redirect(
            url_for(
                "dashboard",
                **_dashboard_appointment_redirect_params(
                    clinic_id, doctor_id, date_str, ["date"],
                ),
            ),
        )

    display_date = parsed.strftime("%d.%m.%Y")

    appt = Appointment(
        system._next_appointment_id(),
        patient.id,
        doctor.id,
        clinic.clinic_id,
        display_date,
    )
    system.appointments.append(appt)
    patient.appointments.append(appt.appointment_id)

    flash(
        f"Запись создана: {doctor.full_name}, {clinic.clinic_name}, {display_date}",
        "success",
    )
    return redirect(url_for("history"))


# ------------------------------------------------------------------ #
#  История записей                                                    #
# ------------------------------------------------------------------ #

@app.route("/history")
@login_required
def history():
    patient = _current_patient()
    records = []
    for a in system.appointments:
        if a.patient_id == patient.id:
            doctor = system._find_doctor_by_id(a.doctor_id)
            clinic = system._find_clinic_by_id(a.clinic_id)
            records.append({
                "appointment": a,
                "doctor": doctor,
                "clinic": clinic,
            })
    return render_template(
        "history.html", records=records, patient=patient,
        today=date.today().isoformat(),
    )


@app.route("/cancel/<int:appointment_id>", methods=["PUT"])
@login_required
def cancel_appointment(appointment_id):
    patient = _current_patient()
    for appt in system.appointments:
        if appt.appointment_id == appointment_id and appt.patient_id == patient.id:
            if appt.status == "cancelled":
                return jsonify(
                    success=False, message="Запись уже отменена.",
                ), 400
            appt.status = "cancelled"
            flash(f"Запись #{appointment_id} отменена.", "success")
            return jsonify(success=True, redirect_url=url_for("history"))
    return jsonify(success=False, message="Запись не найдена."), 400


@app.route("/reschedule/<int:appointment_id>", methods=["PUT"])
@login_required
def reschedule_appointment(appointment_id):
    patient = _current_patient()
    new_date = request.form.get("new_date", "").strip()

    if not new_date:
        return jsonify(success=False, message="Введите новую дату."), 400

    try:
        parsed = datetime.strptime(new_date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify(success=False, message="Неверный формат даты."), 400

    if parsed < date.today():
        return jsonify(
            success=False, message="Дата не может быть раньше сегодняшнего дня.",
        ), 400

    display_date = parsed.strftime("%d.%m.%Y")

    for appt in system.appointments:
        if appt.appointment_id == appointment_id and appt.patient_id == patient.id:
            if appt.status != "scheduled":
                return jsonify(
                    success=False,
                    message="Можно перенести только запланированную запись.",
                ), 400
            appt.date = display_date
            flash(f"Запись #{appointment_id} перенесена на {display_date}.", "success")
            return jsonify(success=True, redirect_url=url_for("history"))

    return jsonify(success=False, message="Запись не найдена."), 400


# ------------------------------------------------------------------ #
#  Настройки безопасности                                             #
# ------------------------------------------------------------------ #

@app.route("/security")
@login_required
def security():
    return render_template("security.html", patient=_current_patient())


@app.route("/update_profile", methods=["PUT"])
@login_required
def update_profile():
    patient = _current_patient()
    last_name = request.form.get("last_name", "").strip()
    first_name = request.form.get("first_name", "").strip()
    middle_name = request.form.get("middle_name", "").strip()
    current_password = request.form.get("current_password", "")

    if current_password != patient.password:
        return jsonify(
            success=False, message="Неверный пароль. Изменение отклонено.",
        ), 400

    if not last_name or not first_name:
        return jsonify(
            success=False, message="Фамилия и имя не могут быть пустыми.",
        ), 400

    patient.edit(last_name=last_name, first_name=first_name, middle_name=middle_name)
    flash("Данные профиля обновлены.", "success")
    return jsonify(success=True, redirect_url=url_for("security"))


@app.route("/update_password", methods=["PUT"])
@login_required
def update_password():
    patient = _current_patient()
    current = request.form.get("current_password", "")
    new_pwd = request.form.get("new_password", "")
    confirm = request.form.get("confirm_password", "")

    if current != patient.password:
        return jsonify(success=False, message="Неверный текущий пароль."), 400

    pwd_ok, pwd_errors = validate_password(new_pwd)
    if not pwd_ok:
        return jsonify(
            success=False,
            message="Пароль не соответствует требованиям: " + "; ".join(pwd_errors),
        ), 400

    if new_pwd != confirm:
        return jsonify(success=False, message="Пароли не совпадают."), 400

    patient.edit(password=new_pwd)
    flash("Пароль успешно изменён.", "success")
    return jsonify(success=True, redirect_url=url_for("security"))


# ------------------------------------------------------------------ #
#  Админ-панель                                                       #
# ------------------------------------------------------------------ #

def _count_admins():
    return sum(1 for p in system.patients if getattr(p, "role", "user") == "admin")


def _try_admin_edit_patient(patient):
    """Читает request.form и обновляет пациента. None — успех, иначе текст ошибки."""
    last_name = request.form.get("last_name", "").strip()
    first_name = request.form.get("first_name", "").strip()
    middle_name = request.form.get("middle_name", "").strip()
    age_str = request.form.get("age", "").strip()
    email = request.form.get("email", "").strip()
    new_role = request.form.get("role", "user").strip()
    password = request.form.get("password", "")

    if not last_name or not first_name:
        return "Фамилия и имя обязательны."

    try:
        age = int(age_str)
        if age <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return "Возраст должен быть положительным числом."

    email_ok, email_err = validate_email(email)
    if not email_ok:
        return email_err

    existing = system.find_patient_by_email(email)
    if existing and existing.id != patient.id:
        return "Этот email уже зарегистрирован."

    if getattr(patient, "role", "user") == "admin" and new_role != "admin":
        if _count_admins() <= 1:
            return "Невозможно понизить последнего администратора."

    pwd_update = None
    if password:
        ok, pwd_errors = validate_password(password)
        if not ok:
            return "Пароль не соответствует требованиям: " + "; ".join(pwd_errors)
        pwd_update = password

    patient.edit(
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
        age=age,
        email=email,
        role=new_role,
        password=pwd_update,
    )
    return None


@app.route("/admin")
@admin_required
def admin():
    return render_template("admin.html", patients=system.patients)


@app.route("/admin/edit/<patient_id>", methods=["GET", "PUT"])
@admin_required
def admin_edit(patient_id):
    patient = system.find_patient_by_id(patient_id)
    if not patient:
        if request.method == "PUT":
            return jsonify(success=False, message="Пациент не найден."), 400
        flash("Пациент не найден.", "error")
        return redirect(url_for("admin"))

    if request.method == "PUT":
        err = _try_admin_edit_patient(patient)
        if err:
            return jsonify(success=False, message=err), 400
        flash(f"Данные пациента {patient.full_name} обновлены.", "success")
        return jsonify(success=True, redirect_url=url_for("admin"))

    return render_template("admin_edit.html", patient=patient)


@app.route("/admin/delete/<patient_id>", methods=["DELETE"])
@admin_required
def admin_delete(patient_id):
    patient = system.find_patient_by_id(patient_id)
    if not patient:
        return jsonify(success=False, message="Пациент не найден."), 400

    if getattr(patient, "role", "user") == "admin" and _count_admins() <= 1:
        return jsonify(
            success=False, message="Невозможно удалить последнего администратора.",
        ), 400

    full_name = patient.full_name
    pid = patient.id

    system.appointments = [
        a for a in system.appointments if a.patient_id != patient.id
    ]
    system.patients.remove(patient)

    if session.get("patient_id") == patient_id:
        session.pop("patient_id", None)

    flash(f"Пациент {full_name} ({pid}) и все его записи удалены.", "success")
    return jsonify(success=True, redirect_url=url_for("admin"))


# ------------------------------------------------------------------ #
#  Сохранение / загрузка                                              #
# ------------------------------------------------------------------ #

@app.route("/save", methods=["GET", "POST"])
@admin_required
def save():
    if request.method == "POST":
        raw_name = request.form.get("filename", "").strip()
        raw_ext = request.form.get("extension", "").strip()
        path = manual_backup_path(raw_name, raw_ext)
        ok, msg = save_system_to_path(system, path)
        if ok:
            flash(f"Данные сохранены в '{path}'.", "success")
        else:
            flash(msg, "error")

        return redirect(url_for("save"))

    return render_template(
        "save_load.html",
        mode="save",
        primary_save_path=DEFAULT_SAVE_PATH,
        default_manual_path=manual_backup_path("", ""),
    )


@app.route("/load", methods=["GET", "POST"])
@admin_required
def load():
    if request.method == "POST":
        raw_name = request.form.get("filename", "").strip()
        raw_ext = request.form.get("extension", "").strip()
        path = manual_backup_path(raw_name, raw_ext)
        data, msg = system.storage.load(path)
        if data is not None and isinstance(data, dict):
            system.patients = data.get("patients", [])
            system.doctors = data.get("doctors", [])
            system.clinics = data.get("clinics", [])
            system.appointments = data.get("appointments", [])
            system._ensure_demo_data()
            flash(f"Данные загружены из '{path}'.", "success")
        elif data is not None:
            flash("Файл повреждён или имеет неверный формат (ожидался словарь).", "error")
        else:
            flash(msg, "error")

        return redirect(url_for("load"))

    return render_template(
        "save_load.html",
        mode="load",
        primary_save_path=DEFAULT_SAVE_PATH,
        default_manual_path=manual_backup_path("", ""),
    )


# ------------------------------------------------------------------ #
#  Запуск                                                             #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    app.run(debug=True, port=8080)
