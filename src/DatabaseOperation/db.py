import sqlite3
import hashlib
import os


class DataBase:
    def __init__(self, db_filename='Test.db'):
        self.db_filename = db_filename
        self.conn = None

    def __enter__(self):
        self._existing()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def _hash_pass(self, passwd):
        """
            hashuje piny żeby porównać z zapisanym w bazie
        """
        # pin = 1234 # default zapisany w bazie
        hasher = hashlib.sha256()
        hasher.update(bytes(str(passwd), encoding="utf-8"))
        return hasher.hexdigest()

    def _existing(self):
        if not os.path.exists(self.db_filename):
            self.conn = sqlite3.connect(self.db_filename)
            print('No schema exists.')
            self.conn.execute('''CREATE TABLE PASSWD_VERIFICATION
                 (ID INT     NOT NULL,
                 USER           TEXT    NOT NULL,
                 PASSWORD             TEXT     NOT NULL);''')
            self.conn.commit()
            self.conn.execute('''CREATE TABLE RECORDS
                 (ID INT     NOT NULL,
                 USER           TEXT    NOT NULL,
                 PIN             TEXT     NOT NULL);''')
            self.conn.commit()
            print("Table created successfully")
            self.conn.execute(f"INSERT INTO PASSWD_VERIFICATION (ID, USER, PASSWORD) VALUES (1, 'JohnDoe', '{self._hash_pass('pass')}')")
            self.conn.commit()
            self.conn.execute("INSERT INTO RECORDS (ID, USER, PIN) VALUES (1, 'JohnDoe', '123#')")
            self.conn.commit()
        else:
            self.conn = sqlite3.connect(self.db_filename)
            print('DB exists.')

    def add_password(self, user='Name', passwd="0000"):
        self.conn.execute(f"INSERT INTO PASSWD_VERIFICATION (ID, USER, PASSWORD) VALUES (1, '{user}', '{self._hash_pass(passwd)}')")
        self.conn.commit()

    def read_password(self, user):
        print('checking in db')
        cursor = self.conn.cursor()
        cursor.execute(f"select ID, USER, PASSWORD from PASSWD_VERIFICATION where USER='{user}'")
        for ID, USER, PASSWORD in cursor.fetchall():
            return ID, USER, PASSWORD

    def read_record(self, user):
        print('checking in db')
        cursor = self.conn.cursor()
        cursor.execute(f"select ID, USER, PIN from RECORDS where USER='{user}'")
        for ID, USER, PIN in cursor.fetchall():
            return ID, USER, PIN


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


class Proxy:
    proxy_state = None
    proxy_state_pin = None

    def __init__(self, db_object):
        self.db_object = db_object


@singleton
class DatabaseProxy(Proxy):
    def read_password(self, user):
        if self.proxy_state is None:
            self.db_object._existing()
            self.proxy_state = self.db_object.read_password(user)
        return self.proxy_state

    def read_record(self, user):
        if self.proxy_state is None:
            self.db_object._existing()
            self.proxy_state_pin = self.db_object.read_record(user)
        return self.proxy_state_pin

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_object.conn.close()

class Check:
    def __init__(self, name, passwd):
        self.name = name
        self.passwd = passwd
        with DatabaseProxy(DataBase()) as read:
            self.record = read.read_record(name)

    @property
    def verified(self):
        if self.record is not None:
            return self.record[2] == self.passwd
        return False