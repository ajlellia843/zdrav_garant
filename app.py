"""Веб-точка входа приложения «ЗдравГарант» на Flask.

Использует MedicalSystem как сервис данных.
Консольная версия (main.py) остаётся без изменений.
"""

import os
import functools
from datetime import datetime, date

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash,
)

from medical_system import MedicalSystem
from patient import Patient
from appointment import Appointment
from validators import validate_password, validate_email

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "zdrav-garant-secret-key")

system = MedicalSystem()


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
        patient = Patient(pid, last_name, first_name, age, password, email, middle_name)
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

    selected_clinic = None
    doctors = []
    if selected_clinic_id:
        selected_clinic = system._find_clinic_by_id(selected_clinic_id)
        if selected_clinic:
            doctors = [d for d in system.doctors if d.clinic_id == selected_clinic_id]

    return render_template(
        "dashboard.html",
        clinics=system.clinics,
        selected_clinic=selected_clinic,
        doctors=doctors,
        patient=patient,
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
        return redirect(url_for("dashboard", clinic_id=clinic_id))

    clinic = system._find_clinic_by_id(clinic_id)
    if not clinic:
        flash("Клиника не найдена.", "error")
        return redirect(url_for("dashboard"))

    doctor = system._find_doctor_by_id(doctor_id)
    if not doctor or doctor.clinic_id != clinic_id:
        flash("Врач не найден в выбранной клинике.", "error")
        return redirect(url_for("dashboard", clinic_id=clinic_id))

    try:
        parsed = datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        flash("Неверный формат даты. Используйте ДД.ММ.ГГГГ.", "error")
        return redirect(url_for("dashboard", clinic_id=clinic_id))

    if parsed < date.today():
        flash("Дата не может быть раньше сегодняшнего дня.", "error")
        return redirect(url_for("dashboard", clinic_id=clinic_id))

    appt = Appointment(
        system._next_appointment_id(),
        patient.id,
        doctor.id,
        clinic.clinic_id,
        date_str,
    )
    system.appointments.append(appt)
    patient.appointments.append(appt.appointment_id)

    flash(
        f"Запись создана: {doctor.full_name}, {clinic.clinic_name}, {date_str}",
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
    return render_template("history.html", records=records, patient=patient)


@app.route("/cancel/<int:appointment_id>", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    patient = _current_patient()
    for appt in system.appointments:
        if appt.appointment_id == appointment_id and appt.patient_id == patient.id:
            if appt.status == "cancelled":
                flash("Запись уже отменена.", "error")
            else:
                appt.status = "cancelled"
                flash(f"Запись #{appointment_id} отменена.", "success")
            return redirect(url_for("history"))
    flash("Запись не найдена.", "error")
    return redirect(url_for("history"))


@app.route("/reschedule/<int:appointment_id>", methods=["POST"])
@login_required
def reschedule_appointment(appointment_id):
    patient = _current_patient()
    new_date = request.form.get("new_date", "").strip()

    if not new_date:
        flash("Введите новую дату.", "error")
        return redirect(url_for("history"))

    try:
        parsed = datetime.strptime(new_date, "%d.%m.%Y").date()
    except ValueError:
        flash("Неверный формат даты. Используйте ДД.ММ.ГГГГ.", "error")
        return redirect(url_for("history"))

    if parsed < date.today():
        flash("Дата не может быть раньше сегодняшнего дня.", "error")
        return redirect(url_for("history"))

    for appt in system.appointments:
        if appt.appointment_id == appointment_id and appt.patient_id == patient.id:
            if appt.status != "scheduled":
                flash("Можно перенести только запланированную запись.", "error")
            else:
                appt.date = new_date
                flash(f"Запись #{appointment_id} перенесена на {new_date}.", "success")
            return redirect(url_for("history"))

    flash("Запись не найдена.", "error")
    return redirect(url_for("history"))


# ------------------------------------------------------------------ #
#  Настройки безопасности                                             #
# ------------------------------------------------------------------ #

@app.route("/security")
@login_required
def security():
    return render_template("security.html", patient=_current_patient())


@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    patient = _current_patient()
    last_name = request.form.get("last_name", "").strip()
    first_name = request.form.get("first_name", "").strip()
    middle_name = request.form.get("middle_name", "").strip()
    current_password = request.form.get("current_password", "")

    if current_password != patient.password:
        flash("Неверный пароль. Изменение отклонено.", "error")
        return redirect(url_for("security"))

    if not last_name or not first_name:
        flash("Фамилия и имя не могут быть пустыми.", "error")
        return redirect(url_for("security"))

    patient.edit(last_name=last_name, first_name=first_name, middle_name=middle_name)
    flash("Данные профиля обновлены.", "success")
    return redirect(url_for("security"))


@app.route("/update_password", methods=["POST"])
@login_required
def update_password():
    patient = _current_patient()
    current = request.form.get("current_password", "")
    new_pwd = request.form.get("new_password", "")
    confirm = request.form.get("confirm_password", "")

    if current != patient.password:
        flash("Неверный текущий пароль.", "error")
        return redirect(url_for("security"))

    pwd_ok, pwd_errors = validate_password(new_pwd)
    if not pwd_ok:
        flash("Пароль не соответствует требованиям: " + "; ".join(pwd_errors), "error")
        return redirect(url_for("security"))

    if new_pwd != confirm:
        flash("Пароли не совпадают.", "error")
        return redirect(url_for("security"))

    patient.edit(password=new_pwd)
    flash("Пароль успешно изменён.", "success")
    return redirect(url_for("security"))


# ------------------------------------------------------------------ #
#  Админ-панель                                                       #
# ------------------------------------------------------------------ #

@app.route("/admin")
def admin():
    return render_template("admin.html", patients=system.patients)


@app.route("/admin/delete/<patient_id>", methods=["POST"])
def admin_delete(patient_id):
    patient = system.find_patient_by_id(patient_id)
    if not patient:
        flash("Пациент не найден.", "error")
        return redirect(url_for("admin"))

    system.appointments = [
        a for a in system.appointments if a.patient_id != patient.id
    ]
    system.patients.remove(patient)

    if session.get("patient_id") == patient_id:
        session.pop("patient_id", None)

    flash(f"Пациент {patient.full_name} ({patient.id}) и все его записи удалены.", "success")
    return redirect(url_for("admin"))


# ------------------------------------------------------------------ #
#  Сохранение / загрузка                                              #
# ------------------------------------------------------------------ #

@app.route("/save", methods=["GET", "POST"])
def save():
    if request.method == "POST":
        raw_name = request.form.get("filename", "").strip()
        raw_ext = request.form.get("extension", "").strip()

        name = raw_name if raw_name else "zdrav_garant"
        ext = raw_ext.lstrip(".") if raw_ext else "pkl"
        filename = f"{name}.{ext}"

        data = {
            "patients": system.patients,
            "doctors": system.doctors,
            "clinics": system.clinics,
            "appointments": system.appointments,
        }
        ok, msg = system.storage.save(data, filename)
        if ok:
            flash(f"Данные сохранены в '{filename}'.", "success")
        else:
            flash(msg, "error")

        return redirect(url_for("save"))

    return render_template("save_load.html", mode="save")


@app.route("/load", methods=["GET", "POST"])
def load():
    if request.method == "POST":
        raw_name = request.form.get("filename", "").strip()
        raw_ext = request.form.get("extension", "").strip()

        name = raw_name if raw_name else "zdrav_garant"
        ext = raw_ext.lstrip(".") if raw_ext else "pkl"
        filename = f"{name}.{ext}"

        data, msg = system.storage.load(filename)
        if data is not None:
            system.patients = data.get("patients", [])
            system.doctors = data.get("doctors", [])
            system.clinics = data.get("clinics", [])
            system.appointments = data.get("appointments", [])
            system._ensure_demo_data()
            flash(f"Данные загружены из '{filename}'.", "success")
        else:
            flash(msg, "error")

        return redirect(url_for("load"))

    return render_template("save_load.html", mode="load")


# ------------------------------------------------------------------ #
#  Запуск                                                             #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    app.run(debug=True)
