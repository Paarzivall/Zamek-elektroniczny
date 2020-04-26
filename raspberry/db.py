import sqlite3
import os
import getpass


class DataBase:
    def __init__(self, db_filename='Test.db'):
        self.db_filename = db_filename
        self.conn = None

    def __enter__(self):
        self._existing()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def _existing(self):
        if not os.path.exists(self.db_filename):
            self.conn = sqlite3.connect(self.db_filename)
            print('No schema exists.')
            self.conn.execute('''CREATE TABLE RECORDS
                 (ID INT     NOT NULL,
                 USER           TEXT    NOT NULL,
                 PIN             TEXT     NOT NULL);''')
            self.conn.commit()
            print("Table created successfully")
            self.conn.execute("INSERT INTO RECORDS (ID, USER, PIN) VALUES (1, 'JohnDoe', '123#')")
            self.conn.commit()
        else:
            self.conn = sqlite3.connect(self.db_filename)
            print('DB exists.')

    def add_record(self, user='Name', pin="0000"):
        self.conn.execute(f"INSERT INTO RECORDS (ID, USER, PIN) VALUES (1, '{user}', '{pin}')")
        self.conn.commit()

    def read_record(self, user):
        print('checking in db')
        cursor = self.conn.cursor()
        cursor.execute(f"select ID, USER, PIN from RECORDS where USER='{user}'")
        for ID, USER, PIN in cursor.fetchall():
            return ID, USER, PIN
        #print("Operation done successfully")


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


class Proxy:
    proxy_state = None

    def __init__(self, db_object):
        self.db_object = db_object


@singleton
class DatabaseProxy(Proxy):
    def read_record(self, user):
        if self.proxy_state is None:
            self.db_object._existing()
            self.proxy_state = self.db_object.read_record(user)
        return self.proxy_state

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


def main():
    while True:
        user = input('User: ')
        pin = getpass.getpass('Pin: ')
        user_verification = Check(user, pin)
        user_verified = user_verification.verified
        print(f"user {user} verified: {user_verified}")


if __name__ == "__main__":
    main()
