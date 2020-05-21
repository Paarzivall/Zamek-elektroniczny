"""
Main method to management password recognize spoken by user
"""

import speech_recognition as sr
import sqlite3 as lite
import hashlib


class Spreech(object):
    def __init__(self):
        """
        Init this module. Can have a lot of instances
        """
        self.recognizer = sr.Recognizer()

    def controller(self):
        """
        main method of this class. Management recognization of password

        :return: True if password is valid or False if is not
        :rtype: bool
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
        :rtype: hasher
        """
        try:
            hasher = hashlib.sha256()
            hasher.update(bytes(str(pin.lower()), encoding="utf-8"))
            return hasher.hexdigest()
        except AttributeError:
            return None

    def get_password(self):
        """
        get password from database

        :return: password
        ::rtype: string
        """
        # pin = self.hash_pin("litwo ojczyzno moja") # default password
        con = lite.connect('databases/zamek_elektroniczny.db')

        cur = con.cursor()
        cur.execute("select ID, PASSWORD FROM spreech_password")
        return str(cur.fetchall()[0][1])

    def listen_spreech(self, source):
        """
        listening sounds from microphone and recognize using google API

        :param source: microphone object
        :type source: spreech_recognition.Microphone()
        :return: converted voice
        :rtype: string
        """
        try:
            audio = self.recognizer.listen(source)
            user = self.recognizer.recognize_google(audio, language="pl-PL")
            return str(user)
        except sr.UnknownValueError:
            # tutaj jakby mikrofon wykrył jakiś dziwny dźwięk ma nie robić nic
            pass
