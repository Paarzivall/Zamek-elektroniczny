import speech_recognition as sr
import sqlite3 as lite
import hashlib


class Spreech(object):
    """
    initialize recognition operation
    """
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def controller(self):
        """
        method to control operations
        :return: True if password is valid or False if is not
        """
        with sr.Microphone() as source:
            while 1:
                if self.hash_password(self.listen_spreech(source)) == self.get_password():
                    return True
                else:
                    return False

    def hash_password(self, pin):
        """
        method who hashing voice sample to checking in database
        :param pin: converted voice sample to check
        :return: hashing password
        """
        try:
            hasher = hashlib.sha256()
            hasher.update(bytes(str(pin.lower()), encoding="utf-8"))
            return hasher.hexdigest()
        except AttributeError:
            return None

    def get_password(self):
        """
        :return: password from database
        """
        # pin = self.hash_pin("litwo ojczyzno moja") # default password
        con = lite.connect('databases/zamek_elektroniczny.db')

        cur = con.cursor()
        cur.execute("select ID, PASSWORD FROM spreech_password")
        return str(cur.fetchall()[0][1])

    def listen_spreech(self, source):
        """

        :param source: microphone object
        :return: converted voice to string
        """
        try:
            audio = self.recognizer.listen(source)
            user = self.recognizer.recognize_google(audio, language="pl-PL")
            return str(user)
        except sr.UnknownValueError:
            # tutaj jakby mikrofon wykrył jakiś dziwny dźwięk ma nie robić nic
            pass

if __name__ == '__main__':
    ss = Spreech()
    print(ss.controller())
