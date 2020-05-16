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
            hashuje piny żeby porównać z zapisanym w bazie
        """
        hasher = hashlib.sha256()
        hasher.update(bytes(str(passwd), encoding="utf-8"))
        return hasher.hexdigest()

    @property
    def passwd(self):
        return self._passwd

    @passwd.setter
    def passwd(self, passwd):
        self._passwd = self._hash_pass(passwd)

    def __verify(self):
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
        self.__verify()
        return self._verified


if __name__ == '__main__':
    user = UserPasswordVerification('JohnDoe', 'pass')
    print(user.passwd)
    print(user.verified)