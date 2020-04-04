import sqlite3 as lite
import hashlib
from sqlite3 import Error


class Option_1_Actions(object):
    def __init__(self, pin):
        self.pin = pin

        #self.add_to_db()

    def hash_pin(self):
        pin = 1234
        hasher = hashlib.sha256()
        hasher.update(bytes(str(pin), encoding="utf-8"))
        return hasher.hexdigest()

    def add_to_db(self):
        pin = self.hash_pin()
        print(pin)
        con = lite.connect('../databases/zamek_elektroniczny.db')
        cur = con.cursor()
        cur.execute("CREATE TABLE pins_for_option_1 (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,PIN TEXT NOT NULL);")
        cur.execute("insert into pins_for_option_1(pin) values('" + str(pin) + "');")
        cur.close()
        cur = con.cursor()
        cur.execute("select * from pins_for_option_1;")
        print(str(cur.fetchall()))

    def connect(self):
        con = lite.connect('../databases/zamek_elektroniczny.db')
        cur = con.cursor()
        cur.execute("select * from pins_for_option_1;")
        # cur.execute("SELECT SQLITE_VERSION();")
        print(cur.fetchall())
        cur.close()

    def create_connection(self, db_file):
        conn = None
        try:
            conn = lite.connect(db_file)
            print(lite.version)
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    def get_pin(self):
        return self.pin

"""
to jest pod moje próby, taki output:

03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4
[(1, '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4')]
[]



a = Option_1_Actions(123)
# a.create_connection(r"C:/Users/mateu/Documents/GitHub/Zamek-elektroniczny/databases/zamek_elektroniczny.db")
a.add_to_db()
a.connect()
"""