import sqlite3 as lite
import hashlib


class Option_1_Actions(object):
    def __init__(self, pin):
        self.pin = self.hash_pin(pin)

    def hash_pin(self, pin):
        """
            hashuje piny żeby porównać z zapisanym w bazie
        """
        # pin = 1234 # default zapisany w bazie
        hasher = hashlib.sha256()
        hasher.update(bytes(str(pin), encoding="utf-8"))
        return hasher.hexdigest()

    def add_to_db(self):
        """
            tutaj będzie update'owanie pinu do bazy, teraz jest tylko dodawanie.
            Wystarczy przerobić polecenie
        """
        pin = self.hash_pin()
        print(pin)
        con = lite.connect('../databases/zamek_elektroniczny.db')
        # con.execute("CREATE TABLE pins_for_option_1 (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,PIN TEXT NOT NULL);")
        con.execute("insert into pins_for_option_1(pin) values('" + str(pin) + "');")
        con.commit()

    def is_correct(self):
        con = lite.connect('../databases/zamek_elektroniczny.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM pins_for_option_1 WHERE pin ='" + str(self.pin) + "';")
        tmp = cur.fetchall()
        cur.close()
        if len(str(tmp)) > 2:
            return True
        else:
            return False

    def get_pin(self):
        return self.pin

