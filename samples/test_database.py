import pytest
from unittest.mock import MagicMock
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from database import get_db_connection, add_trip_details, save_messages, get_chat_history

def test_normal_get_db_connection(monkeypatch):
    mock_conn = MagicMock()
    monkeypatch.setattr('psycopg2.connect', lambda *args, **kwargs: mock_conn)
    result = get_db_connection()
    assert result == mock_conn

def test_edge_case_empty_db_name_get_db_connection(monkeypatch):
    mock_conn = MagicMock()
    monkeypatch.setattr('os.getenv', lambda *args, **kwargs: '')
    monkeypatch.setattr('psycopg2.connect', lambda *args, **kwargs: mock_conn)
    result = get_db_connection()
    assert result == mock_conn

def test_edge_case_empty_db_user_get_db_connection(monkeypatch):
    mock_conn = MagicMock()
    monkeypatch.setattr('os.getenv', lambda name, default: '' if name == 'DB_USER' else default)
    monkeypatch.setattr('psycopg2.connect', lambda *args, **kwargs: mock_conn)
    result = get_db_connection()
    assert result == mock_conn

def test_edge_case_empty_db_password_get_db_connection(monkeypatch):
    mock_conn = MagicMock()
    monkeypatch.setattr('os.getenv', lambda name, default: '' if name == 'DB_PASSWORD' else default)
    monkeypatch.setattr('psycopg2.connect', lambda *args, **kwargs: mock_conn)
    result = get_db_connection()
    assert result == mock_conn

def test_edge_case_empty_db_host_get_db_connection(monkeypatch):
    mock_conn = MagicMock()
    monkeypatch.setattr('os.getenv', lambda name, default: '' if name == 'DB_HOST' else default)
    monkeypatch.setattr('psycopg2.connect', lambda *args, **kwargs: mock_conn)
    result = get_db_connection()
    assert result == mock_conn

def test_edge_case_empty_db_port_get_db_connection(monkeypatch):
    mock_conn = MagicMock()
    monkeypatch.setattr('os.getenv', lambda name, default: '' if name == 'DB_PORT' else default)
    monkeypatch.setattr('psycopg2.connect', lambda *args, **kwargs: mock_conn)
    result = get_db_connection()
    assert result == mock_conn

def test_exception_get_db_connection(monkeypatch):
    mock_exception = Exception('Test exception')
    monkeypatch.setattr('psycopg2.connect', lambda *args, **kwargs: (lambda: mock_exception)())
    try:
        get_db_connection()
        assert False
    except Exception as e:
        assert repr(e) == repr(mock_exception)

def test_normal_case_add_trip_details(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    assert add_trip_details('New York', 'Sunny', 'Backpack') == 1
    mock_cursor.execute.assert_called_once_with('INSERT INTO trips(city, weather, essentials) VALUES (%s,%s,%s) RETURNING id', ('New York', 'Sunny', 'Backpack'))
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

def test_empty_city_add_trip_details(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    assert add_trip_details('', 'Sunny', 'Backpack') == 1
    mock_cursor.execute.assert_called_once_with('INSERT INTO trips(city, weather, essentials) VALUES (%s,%s,%s) RETURNING id', ('', 'Sunny', 'Backpack'))
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

def test_empty_weather_add_trip_details(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    assert add_trip_details('New York', '', 'Backpack') == 1
    mock_cursor.execute.assert_called_once_with('INSERT INTO trips(city, weather, essentials) VALUES (%s,%s,%s) RETURNING id', ('New York', '', 'Backpack'))
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

def test_empty_essentials_add_trip_details(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    assert add_trip_details('New York', 'Sunny', '') == 1
    mock_cursor.execute.assert_called_once_with('INSERT INTO trips(city, weather, essentials) VALUES (%s,%s,%s) RETURNING id', ('New York', 'Sunny', ''))
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

def test_exception_add_trip_details(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception('Test exception')
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    try:
        add_trip_details('New York', 'Sunny', 'Backpack')
        assert False
    except Exception as e:
        assert repr(e) == repr(Exception('Test exception'))
    mock_conn.close.assert_called_once()

def test_fetchone_none_add_trip_details(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    try:
        add_trip_details('New York', 'Sunny', 'Backpack')
        assert False
    except TypeError:
        pass
    mock_cursor.execute.assert_called_once_with('INSERT INTO trips(city, weather, essentials) VALUES (%s,%s,%s) RETURNING id', ('New York', 'Sunny', 'Backpack'))
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

def test_normal_case_save_messages(monkeypatch):
    mock_conn = MagicMock()
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    save_messages(1, 'driver', 'hello')
    mock_conn.cursor.assert_called_once()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.execute.assert_called_once_with('INSERT INTO chat_history (trip_id, role, message) VALUES (%s,%s,%s)', (1, 'driver', 'hello'))
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

def test_edge_case_empty_message_save_messages(monkeypatch):
    mock_conn = MagicMock()
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    save_messages(1, 'driver', '')
    mock_conn.cursor.assert_called_once()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.execute.assert_called_once_with('INSERT INTO chat_history (trip_id, role, message) VALUES (%s,%s,%s)', (1, 'driver', ''))
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

def test_edge_case_long_message_save_messages(monkeypatch):
    mock_conn = MagicMock()
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    save_messages(1, 'driver', 'a' * 1000)
    mock_conn.cursor.assert_called_once()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.execute.assert_called_once_with('INSERT INTO chat_history (trip_id, role, message) VALUES (%s,%s,%s)', (1, 'driver', 'a' * 1000))
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

def test_edge_case_none_message_save_messages(monkeypatch):
    mock_conn = MagicMock()
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    save_messages(1, 'driver', None)
    mock_conn.cursor.assert_called_once()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.execute.assert_called_once_with('INSERT INTO chat_history (trip_id, role, message) VALUES (%s,%s,%s)', (1, 'driver', None))
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

def test_exception_db_connection_save_messages(monkeypatch):
    mock_conn = MagicMock(side_effect=Exception('db connection error'))
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    try:
        save_messages(1, 'driver', 'hello')
        assert False
    except Exception as e:
        assert repr(e) == repr(Exception('db connection error'))

def test_exception_cursor_execution_save_messages(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock(side_effect=Exception('cursor execution error'))
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    try:
        save_messages(1, 'driver', 'hello')
        assert False
    except Exception as e:
        assert repr(e) == repr(Exception('cursor execution error'))

def test_exception_commit_save_messages(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.commit.side_effect = Exception('commit error')
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    try:
        save_messages(1, 'driver', 'hello')
        assert False
    except Exception as e:
        assert repr(e) == repr(Exception('commit error'))

def test_normal_get_chat_history(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [{'role': 'user', 'message': 'hello'}, {'role': 'assistant', 'message': 'hi'}]
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    result = get_chat_history(1)
    assert result == [{'role': 'user', 'message': 'hello'}, {'role': 'assistant', 'message': 'hi'}]

def test_empty_get_chat_history(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    result = get_chat_history(1)
    assert result == []

def test_none_get_chat_history(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = None
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    result = get_chat_history(1)
    assert result is None

def test_exception_get_chat_history(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception('test exception')
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    try:
        get_chat_history(1)
        assert False
    except Exception as e:
        assert repr(e) == repr(Exception('test exception'))

def test_invalid_trip_id_get_chat_history(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception('invalid trip id')
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    try:
        get_chat_history('invalid')
        assert False
    except Exception as e:
        assert repr(e) == repr(Exception('invalid trip id'))

def test_db_connection_error_get_chat_history(monkeypatch):
    mock_conn = MagicMock()
    mock_conn.side_effect = Exception('db connection error')
    monkeypatch.setattr('database.get_db_connection', lambda: mock_conn)
    try:
        get_chat_history(1)
        assert False
    except Exception as e:
        assert repr(e) == repr(Exception('db connection error'))