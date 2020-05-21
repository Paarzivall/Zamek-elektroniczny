import sqlite3
import hashlib
import os


class DataBase:
    """
    This class allows connection to sqlite database with context manager.
    """
    def __init__(self, db_filename='tests/Test.db'):
        """
        Init method of DataBase class.

        :param db_filename: defines path and name of db file
        :type db_filename: str
        """
        self.db_filename = db_filename
        self.conn = None

    def __enter__(self):
        """
        Method enter for context manager. Call _existing method to setup db connection.

        :return: self
        :rtype: DataBase
        """
        self._existing()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    @staticmethod
    def _hash_pass(passwd):
        """
        Return hashed password.

        :param passwd: password to be hashed
        :type passwd: str
        :return: hashed password
        :rtype: str
        """
        # pin = 1234 # default zapisany w bazie
        hasher = hashlib.sha256()
        hasher.update(bytes(str(passwd), encoding="utf-8"))
        return hasher.hexdigest()

    def _existing(self):
        """
        Checks if database with name defined in attribute db_filename exists, if not create new database with needed
        tables and fill tables with default values.

        :return:
        :rtype:
        """
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
        """
        Adds record to table "PASSWD_VERIFICATION" in database.

        :param user: name of the user
        :type user: str
        :param passwd: password of the user
        :type passwd: str
        :return: None
        :rtype: None
        """
        self.conn.execute(f"INSERT INTO PASSWD_VERIFICATION (ID, USER, PASSWORD) VALUES (1, '{user}', '{self._hash_pass(passwd)}')")
        self.conn.commit()

    def read_password(self, user):
        """
        Reads record from the table "PASSWD_VERIFICATION" in database.

        :param user: name of the user
        :type user: str
        :return: tuple with database record
        :rtype: tuple
        """
        print('checking in db')
        cursor = self.conn.cursor()
        cursor.execute(f"select ID, USER, PASSWORD from PASSWD_VERIFICATION where USER='{user}'")
        for ID, USER, PASSWORD in cursor.fetchall():
            return ID, USER, PASSWORD

    def read_record(self, user):
        """
        Read record from the table "RECORDS" in database.

        :param user: name of the user
        :type user: str
        :return: tuple with database record
        :rtype: tuple
        """
        print('checking in db')
        cursor = self.conn.cursor()
        cursor.execute(f"select ID, USER, PIN from RECORDS where USER='{user}'")
        for ID, USER, PIN in cursor.fetchall():
            print(ID, USER, PIN)
            return ID, USER, PIN


def singleton(class_):
    """
    Function for decorating classes which need to be singleton.

    :param class_: Decorated class which needs to be singleton.
    :type class_: object
    :return: instance of class
    :rtype: object
    """
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


class Proxy:
    """
    Abstract class for proxy design pattern.
    """
    proxy_state = None
    proxy_state_pin = None

    def __init__(self, db_object):
        """
        Init method for abstract Proxy class.

        :param db_object: Instance of DataBase class
        :type db_object: DataBase
        """
        self.db_object = db_object


@singleton
class DatabaseProxy(Proxy):
    """
    This class is used for reading password and pin from database with proxy design pattern
    """
    def read_password(self, user):
        """
        Proxy method for reading record with password for a given user.

        :param user: name og the user
        :type user: str
        :return: DataBase record
        :rtype: tuple
        """
        if self.proxy_state is None:
            self.db_object._existing()
            self.proxy_state = self.db_object.read_password(user)

        return self.proxy_state if self.proxy_state is not None and self.proxy_state[1] == user else None

    def read_record(self, user):
        """
        Proxy method for reading record with pin for a given user.

        :param user: name og the user
        :type user: str
        :return: DataBase record
        :rtype: tuple
        """
        if self.proxy_state_pin is None:
            self.db_object._existing()
            self.proxy_state_pin = self.db_object.read_record(user)
        print(f"pin record: {self.proxy_state_pin}")
        return self.proxy_state_pin if self.proxy_state_pin is not None and self.proxy_state_pin[1] == user else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_object.conn.close()


class Check:
    """
    This class is used for checking if user has provided correct pin via keybord attached to Raspberry Pi.
    """
    def __init__(self, name, passwd, db_file='databases/zamek.db'):
        """
        Init method for Check class which is used for pin verification.

        :param name: name og the user
        :type name: str
        :param passwd: password provided by user
        :type passwd: str
        """
        self.name = name
        self.passwd = passwd
        with DatabaseProxy(DataBase(db_file)) as read:
            self.record = read.read_record(self.name)

    @property
    def verified(self):
        """
        Check if password provided by user is equal with password from DataBase.

        :return: verification result
        :rtype: bool
        """
        if self.record is not None:
            return self.record[2] == self.passwd
        return False


if __name__ == "__main__":
    with DatabaseProxy(DataBase('databases/zamek.db')) as db:
        db_record = db.read_password('JohnDoe')
        print(db_record)

    cc = Check('JohnDoe', '123#')
    print(cc.verified)

    with DataBase('databases/zamek.db') as db:
        print(db.read_record('JohnDoe'))
