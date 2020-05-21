import pytest
import sys
import os

sys.path.append('.')

from src.DatabaseOperation.db import Check, DataBase, DatabaseProxy
from src.KeyboardOperation.Option_1_Actions import UserPasswordVerification


def clear_db():
    db_file = os.path.join(os.getcwd(), 'tests/Test.db')
    try:
        os.remove(db_file)
    except FileNotFoundError:
        pass
    return db_file


def clear_proxy():
    DatabaseProxy().proxy_state = None
    DatabaseProxy().proxy_state_pin = None


def test_user_password_verification_none_existing_user():
    db_file = clear_db()
    user = UserPasswordVerification('some_test_user', 'pass', db_file=db_file)
    assert user.passwd == DataBase._hash_pass('pass')
    assert user.verified is False


def test_user_password_verification():
    db_file = clear_db()
    user = UserPasswordVerification('JohnDoe', 'pass', db_file=db_file)
    assert user.passwd == DataBase._hash_pass('pass')
    assert user.verified is True


def test_user_password_verification_none_existing_user_when_proxy_is_not_empty():
    db_file = clear_db()
    user = UserPasswordVerification('some_test_user', 'pass', db_file=db_file)
    assert user.passwd == DataBase._hash_pass('pass')
    assert user.verified is False


def test_database_read_password():
    db_file = clear_db()
    with DataBase(db_file) as db:
        record = db.read_password('JohnDoe')
        assert record[1] == 'JohnDoe'
        assert record[2] == db._hash_pass('pass')


def test_database_read_password_for_unknown_user():
    db_file = clear_db()
    with DataBase(db_file) as db:
        record = db.read_password('some_user')
        assert record is None


def test_database_read_record():
    db_file = clear_db()
    with DataBase(db_file) as db:
        record = db.read_record('JohnDoe')
        assert record[1] == 'JohnDoe'
        assert record[2] == '123#'


def test_database_read_record_for_unknown_user():
    db_file = clear_db()
    with DataBase(db_file) as db:
        record = db.read_record('some_user')
        assert record is None


def test_database_add_passord():
    db_file = clear_db()
    with DataBase(db_file) as db:
        db.add_password('some_user', 'pass123')
        record = db.read_password('some_user')
        assert record[1] == 'some_user'
        assert record[2] == db._hash_pass('pass123')


def test_database_proxy_1():
    db_file = clear_db()
    clear_proxy()
    with DatabaseProxy(DataBase(db_file)) as db:
        assert db.proxy_state_pin is None
        assert db.proxy_state is None
        db.read_record('JohnDoe')
        assert db.proxy_state_pin[1] == 'JohnDoe'
        assert db.proxy_state is None
        db.proxy_state_pin = (1, 'JohnDoe', 'proxy_test')
        record = db.read_record('JohnDoe')
        assert record[2] == 'proxy_test'


def test_database_proxy_2():
    db_file = clear_db()
    with DatabaseProxy(DataBase(db_file)) as db:
        assert db.proxy_state_pin[1] == 'JohnDoe'
        assert db.proxy_state is None
        db.read_password('JohnDoe')
        assert db.proxy_state[1] == 'JohnDoe'
        assert db.proxy_state_pin[2] == 'proxy_test'
        db.proxy_state = (1, 'JohnDoe', 'proxy_test')
        record = db.read_password('JohnDoe')
        assert record[2] == 'proxy_test'
    clear_proxy()


def test_check_class():
    db_file = clear_db()
    clear_proxy()
    test_check = Check('JohnDoe', '123#', db_file=db_file)
    assert test_check.verified is True


def test_check_class_2():
    db_file = clear_db()
    clear_proxy()
    test_check = Check('JohnDoe', '1234', db_file=db_file)
    assert test_check.verified is False






