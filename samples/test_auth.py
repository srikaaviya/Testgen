import pytest
from auth import login, is_strong_password

def test_normal_case_login():
    assert login(username="admin", password="secret") == True

def test_empty_username_login():
    try:
        login(username="", password="secret")
        assert False
    except ValueError as e:
        assert repr(e) == repr(ValueError("Username and password required"))

def test_empty_password_login():
    try:
        login(username="admin", password="")
        assert False
    except ValueError as e:
        assert repr(e) == repr(ValueError("Username and password required"))

def test_empty_both_login():
    try:
        login(username="", password="")
        assert False
    except ValueError as e:
        assert repr(e) == repr(ValueError("Username and password required"))

def test_invalid_credentials_login():
    assert login(username="user", password="pass") == False

def test_invalid_username_login():
    assert login(username="user", password="secret") == False

def test_invalid_password_login():
    assert login(username="admin", password="pass") == False

def test_normal_case_is_strong_password():
    assert is_strong_password("P@ssw0rd") == True

def test_short_password_is_strong_password():
    assert is_strong_password("P@ssw0") == False

def test_no_digit_is_strong_password():
    assert is_strong_password("Password") == False

def test_no_uppercase_is_strong_password():
    assert is_strong_password("p@ssw0rd") == False

def test_empty_password_is_strong_password():
    assert is_strong_password("") == False

def test_only_digit_is_strong_password():
    assert is_strong_password("12345678") == False

def test_only_uppercase_is_strong_password():
    assert is_strong_password("PASSWORD") == False

def test_only_lowercase_is_strong_password():
    assert is_strong_password("password") == False

def test_password_with_special_char_is_strong_password():
    assert is_strong_password("P@ssw0rd!") == True

def test_password_with_whitespace_is_strong_password():
    assert is_strong_password("P@ss w0rd") == True

def test_password_with_non_ascii_char_is_strong_password():
    assert is_strong_password("P@ssw0rdé") == True

def test_password_with_repr_is_strong_password():
    password = repr("P@ssw0rd")
    assert is_strong_password(password[1:-1]) == True