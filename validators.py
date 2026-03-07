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
