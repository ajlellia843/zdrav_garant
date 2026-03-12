"""Модуль с функциями валидации данных."""

import string


def validate_password(password: str) -> tuple[bool, list[str]]:
    """Проверяет пароль на соответствие требованиям сложности.

    Требования:
        - минимум 8 символов;
        - хотя бы одна строчная латинская буква (a-z);
        - хотя бы одна заглавная латинская буква (A-Z);
        - хотя бы одна цифра (0-9);
        - хотя бы один специальный символ.

    Returns:
        Кортеж (пароль_валиден: bool, список_ошибок: list[str]).
    """
    errors: list[str] = []

    if len(password) < 8:
        errors.append("минимум 8 символов")

    if not any(c in string.ascii_lowercase for c in password):
        errors.append("хотя бы одна строчная латинская буква (a-z)")

    if not any(c in string.ascii_uppercase for c in password):
        errors.append("хотя бы одна заглавная латинская буква (A-Z)")

    if not any(c in string.digits for c in password):
        errors.append("хотя бы одна цифра (0-9)")

    special_chars = set(string.punctuation)
    if not any(c in special_chars for c in password):
        errors.append("хотя бы один специальный символ (!@#$%^&* и т.д.)")

    return (len(errors) == 0, errors)


def validate_email(email: str) -> tuple[bool, str]:
    """Проверяет email на базовую корректность.

    Требования:
        - не пустой;
        - без пробелов;
        - содержит ровно один символ @;
        - после @ есть доменная часть с точкой.

    Returns:
        Кортеж (email_валиден: bool, сообщение_об_ошибке: str).
    """
    if not email or not email.strip():
        return False, "Email не может быть пустым."

    if " " in email:
        return False, "Email не должен содержать пробелов."

    if email.count("@") != 1:
        return False, "Email должен содержать ровно один символ @."

    local_part, domain = email.split("@")

    if not local_part:
        return False, "Перед @ должна быть локальная часть."

    if not domain or "." not in domain:
        return False, "После @ должен быть домен с точкой (например, mail.ru)."

    if domain.startswith(".") or domain.endswith("."):
        return False, "Домен не может начинаться или заканчиваться точкой."

    return True, ""
