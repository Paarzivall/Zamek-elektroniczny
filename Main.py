from flask import Flask, render_template, request, redirect, url_for
import time
from src.KeyboardOperation.Option_1_Actions import UserPasswordVerification
from src.CameraOperation.Camera import VideoCamera
from src.SpreechOperation import Spreech
from src.Controller import FailedCounter
# from src.SpreechOperation import SpreechAnalyzer
from src.forms import LoginForm
from raspberry.state import MasterLog, Lock, UserAuthenticationInfo, LockStateInfo, Locked, Unlocked, SetAngle, SetLED
from raspberry.keypad import Keypad
from src.DatabaseOperation.db import Check
app = Flask(__name__)
app.config['SECRET_KEY'] = '00112233445566778899aabbccddeeff'

# licznik pod niepowodzenia logowania
# default ustawiony na 3 niepowodzenia
failed = FailedCounter.FailedCounter.get_instance()


class User:
    def __init__(self, lock, name=None,):
        self.name = name
        self.lock = lock
        self._authentication_time = 0
        self.authentication_timeout = 180
        self._pass_verified = False
        self._face_verified = False
        self._speech_verified = True
        self._pin_verified = True

    @property
    def pass_verified(self) -> bool:
        print(self._authentication_time)
        return self._pass_verified and self._authentication_time + self.authentication_timeout > time.time() and self.name is not None

    @pass_verified.setter
    def pass_verified(self, val):
        print('pass verified setter')
        if val:
            self._pass_verified = val
            self._authentication_time = time.time()
            print('user verified with password')
        else:
            self._pass_verified = val
        self.lock.authentication(UserAuthenticationInfo(self.name, self._pass_verified, 'password'))

    @property
    def face_verified(self) -> bool:
        return self._face_verified and self._authentication_time + self.authentication_timeout > time.time()

    @face_verified.setter
    def face_verified(self, val):
        if val:
            self._face_verified = val
            self._authentication_time = time.time()
        else:
            self._face_verified = val
        self.lock.authentication(UserAuthenticationInfo(self.name, self._face_verified, 'face'))

    @property
    def speech_verified(self) -> bool:
        return self._speech_verified and self._authentication_time + self.authentication_timeout > time.time()

    @speech_verified.setter
    def speech_verified(self, val):
        if val:
            self._speech_verified = val
            self._authentication_time = time.time()
        else:
            self._speech_verified = val
        self.lock.authentication(UserAuthenticationInfo(self.name, self._speech_verified, 'speech'))

    @property
    def pin_verified(self) -> bool:
        return self._pin_verified and self._authentication_time + self.authentication_timeout > time.time()

    @pin_verified.setter
    def pin_verified(self, val):
        if val:
            self._pin_verified = val
            self._authentication_time = time.time()
        else:
            self._pin_verified = val
        self.lock.authentication(UserAuthenticationInfo(self.name, self._speech_verified, 'pin'))

    @property
    def authenticated(self):
        return self.pin_verified and self.speech_verified and self.face_verified and self.pass_verified

    def control_lock(self, state):
        args = LockStateInfo(self.name, state)
        #self.authenticate()
        self.lock.change(state, args)

    def authenticate(self):
        for _ in range(3):
            kp = Keypad(columnCount=3)
            seq = []
            for i in range(4):
                digit = None
                while digit is None:
                    digit = kp.getKey()
                seq.append(digit)
                print(digit)
                time.sleep(0.4)
            _pin = "".join([str(i) for i in seq])
            user_verification = Check(self.name, _pin)
            user_verified = user_verification.verified
            if user_verified:
                self.lock.authentication(UserAuthenticationInfo(self.name, self.authenticated, 'pin'))
                break
            self.lock.authentication(UserAuthenticationInfo(self.name, self.authenticated, 'pin'))



door_lock = Lock('main door')
user = User(door_lock)
master_log = MasterLog(door_lock)


@app.route('/')
@app.route('/main_page')
def main_page():
    """
    :return: main page if failed counter is valid or blocking page if is not
    """
    if failed.is_valid():
        return render_template('main_page.html', title="Main Page", user=user, log=master_log)
    else:
        return redirect(url_for('block'))


@app.route("/password", methods=['GET', 'POST'])
def password_verification():
    """
    Display website with login form. If correct password is submitted redirects to main_page

    :return: form page id failed counter is valid or blocking page if is not
    """
    if failed.is_valid():
        form = LoginForm()
        if form.validate_on_submit():
            user_verification = UserPasswordVerification(form.user.data, form.password.data)
            user.name = user_verification.user
            print(user_verification.verified)
            if user_verification.verified:
                user.pass_verified = True
                return redirect(url_for('main_page'))
            else:
                user.pass_verified = False
                failed.add()
        return render_template('password.html', title="PasswordVerification", form=form, log=master_log)
    else:
        return redirect(url_for('block'))


@app.route("/speech")
def speech_verification():
    """
    Starts speech verification, if speech is verified redirects to main_page

    :return: redirects to main page or block page
    """
    if failed.is_valid():
        spr = Spreech.Spreech()
        if spr.controller() is True:
            user.speech_verified = True
            failed.clear_count()
        else:
            user.speech_verified = False
            failed.add()
        return redirect(url_for('main_page'))
    else:
        return redirect(url_for('block'))


@app.route('/face')
def face_verification():
    """
    Starts face recognition process, if face is verified redirects to main page.

    :return: redirects to main page or block page
    """
    cam = VideoCamera()
    cam.get_frame()
    if cam.action:
        user.face_verified = True
    else:
        user.face_verified = False
        failed.add()

    return redirect(url_for('main_page'))


@app.route("/open")
def open_lock():
    """
    Opens lock.

    :returns: redirects to main page
    """
    if user.authenticated:
        user.control_lock(Unlocked)
    return redirect(url_for('main_page'))


@app.route("/close")
def close_lock():
    """
    Closes lock.

    :returns: redirects to main page
    """
    if user.pass_verified:
        user.control_lock(Locked)

    return redirect(url_for('main_page'))


@app.route("/option4")
def option_fourth():
    if failed.is_valid():
        return render_template('option4.html', title="Option Fourth", show=True)
    else:
        return redirect(url_for('block'))


# @app.route('/verify4', methods=['GET', 'POST'])
# def verify_spreech():
#     spr = Spreech.Spreech()
#     if spr.controller() is True:
#         failed.clear_count()
#         # return render_template('open.html', title="Open", show=True)
#         return option_fourth()
#     else:
#         failed.add()
#         if failed.is_valid():
#             return option_third()
#         else:
#             return redirect(url_for('block'))


@app.route("/block")
def block():
    """

    :return: block page and starting website timeout mechanism
    """
    return render_template('block.html', title="Blocked")


# @app.route('/verify5', methods=['GET', 'POST'])
# def analyze_spreech():
#     """
#
#     :return: page with starter for sound recognize mechanism
#     """
#     spreech = SpreechAnalyzer.SpreechAnalyzer()
#     if spreech.recognize() is True:
#         failed.clear_count()
#         return render_template('open.html', title="Open", show=True)
#     else:
#         failed.add()
#         if failed.is_valid():
#             return option_fourth()
#         else:
#             return block()


if __name__ == '__main__':
    app.run(debug=True)



