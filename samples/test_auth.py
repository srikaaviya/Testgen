import pytest

from auth import login, is_strong_password

def test_normal_login():
    assert login("admin", "secret") == True

def test_empty_username_login():
    try:
        login("", "secret")
        assert False
    except ValueError as e:
        assert repr(e) == repr(ValueError("Username and password required"))

def test_empty_password_login():
    try:
        login("admin", "")
        assert False
    except ValueError as e:
        assert repr(e) == repr(ValueError("Username and password required"))

def test_empty_both_login():
    try:
        login("", "")
        assert False
    except ValueError as e:
        assert repr(e) == repr(ValueError("Username and password required"))

def test_invalid_username_login():
    assert login("user", "secret") == False

def test_invalid_password_login():
    assert login("admin", "wrong") == False

def test_invalid_both_login():
    assert login("user", "wrong") == False

def test_normal_case_is_strong_password():
    assert is_strong_password(repr("P@ssw0rd")) == True

def test_short_password_is_strong_password():
    assert is_strong_password(repr("P@ss")) == False

def test_no_digit_is_strong_password():
    assert is_strong_password(repr("Password")) == False

def test_no_uppercase_is_strong_password():
    assert is_strong_password(repr("password1")) == False

def test_empty_password_is_strong_password():
    assert is_strong_password(repr("")) == False

def test_only_digits_is_strong_password():
    assert is_strong_password(repr("12345678")) == False

def test_only_uppercase_is_strong_password():
    assert is_strong_password(repr("ABCDEFGHIJKLMNOPQRSTUVWXYZ")) == False

def test_only_lowercase_is_strong_password():
    assert is_strong_password(repr("abcdefghijklmnopqrstuvwxyz")) == False

def test_password_with_special_chars_is_strong_password():
    assert is_strong_password(repr("P@ssw0rd!")) == True

def test_password_with_spaces_is_strong_password():
    assert is_strong_password(repr("P@ss w0rd")) == True