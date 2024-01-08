import backend.db_management as db_management
from re import match
from sqlite3 import OperationalError

OPERATION_SUCCESSFUL = 0
EMAIL_ALREADY_EXISTS = 1
DIFFERENT_PASSWORDS = 2
INCORRECT_EMAIL = 3
INCORRECT_PASSWORD = 4
INCORRECT_USERNAME = 5
NONEXISTENT_EMAIL = 6
LOGOUT_SUCCESSFUL = 7


def validate_email(email: str) -> bool:
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(match(email_pattern, email))


def validate_password(password: str) -> bool:
    if len(password) < 8 or \
            not any(char.isupper() for char in password) or \
            not any(char.isnumeric() for char in password):
        return False
    return True


def register(email: str, username: str, password1: str, password2: str) -> int:
    if db_management.select('Uzytkownicy', 'Email', ('Email', email)):
        return EMAIL_ALREADY_EXISTS
    elif password1 != password2:
        return DIFFERENT_PASSWORDS
    elif not validate_email(email):
        return INCORRECT_EMAIL
    elif not validate_password(password1):
        return INCORRECT_PASSWORD
    elif not username:
        return INCORRECT_USERNAME
    db_management.insert('Uzytkownicy', (email, username, password1))
    return OPERATION_SUCCESSFUL


def login(email: str, password: str) -> int:
    try:
        if db_management.select('Uzytkownicy', 'Haslo', ('Email', email)):
            if db_management.select('Uzytkownicy', 'Haslo', ('Email', email))[0] != password:
                return INCORRECT_PASSWORD
        else:
            return NONEXISTENT_EMAIL
    except OperationalError:
        return INCORRECT_EMAIL
    return OPERATION_SUCCESSFUL


def logout(email: str) -> int:
    try:
        if db_management.select('Uzytkownicy', 'Email', ('Email', email)):
            return LOGOUT_SUCCESSFUL
        else:
            return NONEXISTENT_EMAIL
    except OperationalError:
        return INCORRECT_EMAIL
