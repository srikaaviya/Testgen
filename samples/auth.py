def login(username, password):
    if not username or not password:
        raise ValueError("Username and password required")
    if username == "admin" and password == "secret":
        return True
    return False


def is_strong_password(password):
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    return True
