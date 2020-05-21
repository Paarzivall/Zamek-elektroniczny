"""
Class to management connections and operation in database
"""

from src.DatabaseOperation.db import DataBase, DatabaseProxy
import hashlib


class UserPasswordVerification:
    def __init__(self, user, passwd, db_file='databases/zamek.db'):
        self.user = user
        self.passwd = passwd
        self._verified = None
        self.__db_file = db_file

    @staticmethod
    def _hash_pass(passwd):
        """

        :param passwd:
        :return: hashing password
        :rtype: hasher
        """
        hasher = hashlib.sha256()
        hasher.update(bytes(str(passwd), encoding="utf-8"))
        return hasher.hexdigest()

    @property
    def passwd(self):
        """
        getting object of this class

        :return: password
        :rtype: hasher
        """
        return self._passwd

    @passwd.setter
    def passwd(self, passwd):
        """
        setter using to set hashing password as object of this class

        :param passwd: password
        :type passwd: string
        :return: None
        :rtype: None
        """
        self._passwd = self._hash_pass(passwd)

    def __verify(self):
        """
        checking if password is correct: if is setting variable to True else setting to False

        :return: None
        :rtype: None
        """
        self._verified = None
        with DatabaseProxy(DataBase(self.__db_file)) as db:
            db_record = db.read_password(self.user)
            print(db_record)
            if db_record is not None:
                if db_record[-1] == self.passwd:
                    self._verified = True
                else:
                    self._verified = False
            else:
                self._verified = False

    @property
    def verified(self):
        """
        getting information about user

        :return: variable with information about authentication authentication
        :rtype: bool
        """
        self.__verify()
        return self._verified


if __name__ == '__main__':
    user = UserPasswordVerification('JohnDoe', 'pass')
    print(user.passwd)
    print(user.verified)