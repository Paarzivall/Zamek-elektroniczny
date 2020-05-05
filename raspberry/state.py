import RPi.GPIO as GPIO
import time
from raspberry.keypad import Keypad
from raspberry.db import Check
#
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)


def SetAngle(angle):
    offset = 20
    angle = angle + offset
    print(f"setting angle on servo: {angle}")
    if angle < 30:
        SetLED('red')
    else:
        SetLED('green')

    pwm = GPIO.PWM(17, 50)
    pwm.start(0)
    duty = angle / 18 + 2
    GPIO.output(17, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.stop()

def SetLED(color):
    if color == 'red':
        GPIO.output(21, GPIO.LOW)
        GPIO.output(26, GPIO.HIGH)
    if color == 'green':
        GPIO.output(26, GPIO.LOW)
        GPIO.output(21, GPIO.HIGH)

class LockState:
    name = "state"
    allowed = []

    def __init__(self, lock=None):
        self.lock = lock
        if self.lock is not None:
            lock.events.append(self.__lock_log)

    def switch(self, state):
        """ Switch to new state """
        if state.name in self.allowed:
            self.__class__ = state
        else:
            self.__lock_log(f'[LockState Log] Current: {self} => switching to {state.name} not possible.')

    @staticmethod
    def __lock_log(msg):
        if isinstance(msg, str):
            print(msg)

    def __str__(self):
        return self.name


class Locked(LockState):
    name = "locked"
    allowed = ['unlocked']
    servo_angle = 0


class Unlocked(LockState):
    """ State of being powered on and working """
    name = "unlocked"
    allowed = ['locked']
    servo_angle = 90


class Event(list):
    def __call__(self, *args, **kwargs):
        for item in self:
            item(*args, **kwargs)


class LockStateInfo:
    def __init__(self, who_change, lock_action):
        self.who_change_state = who_change
        self.lock_action = lock_action()
        self.lock_name = None


class UserAuthenticationInfo:
    def __init__(self, who, success, level=''):
        self.who = who
        self.success = success
        self.level = level


class Lock:
    """ A class representing a lock """

    def __init__(self, name):
        # State of the lock - default is locked.
        self.name = name
        self.events = Event()
        self.state = Locked(self)
        self.allowed_users = []

    def change(self, state, args=None):
        """ Change state """
        self.state.switch(state)
        if args is not None:
            args.lock_name = self.name
            self.events(args)
        SetAngle(self.state.servo_angle)

    def authentication(self, args):
        self.events(args)


class User:
    authentication_timeout = 30  # s

    def __init__(self, lock, name):
        self.name = name
        self.lock = lock
        self._authenticated = None
        self._authentication_time = None

    @property
    def authenticated(self) -> bool:
        return self._authenticated and self._authentication_time + self.authentication_timeout > time.time()

    @authenticated.setter
    def authenticated(self, val):
        if val:
            self._authenticated = val
            self._authentication_time = time.time()
        else:
            self._authentication_time = None

    def control_lock(self, state):
        if self.name is not None and self.authenticated is True:
            args = LockStateInfo(self.name, state)
            self.lock.change(state, args)
        else:
            self.authenticate()
            self.control_lock(state)

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
                self.authenticated = True
                self.lock.authentication(UserAuthenticationInfo(self.name, self.authenticated))
                break
            self.lock.authentication(UserAuthenticationInfo(self.name, self.authenticated))


class MasterLog:
    def __init__(self, lock):
        lock.events.append(self.save_log)
        self.state_logs = []
        self.auth_logs = []

    def save_log(self, args):
        if isinstance(args, LockStateInfo):
            msg = f'[Master Log] State of lock: {args.lock_name} changed to: {args.lock_action} by: {args.who_change_state}'
            self.state_logs.append(msg)
            print(msg)
        elif isinstance(args, UserAuthenticationInfo):
            msg = f'[Authentication Log] User {args.who} tried to log in with success: {args.success}, ' \
                  f'auth-level: {args.level}'
            self.auth_logs.append(msg)
            print(msg)


if __name__ == "__main__":
    door_lock = Lock('main door')
    MasterLog(door_lock)


    # door_lock.change(Locked)
    # time.sleep(5)
    # door_lock.change(Unlocked)
    # time.sleep(5)
    # door_lock.change(Unlocked)
    # time.sleep(5)
    # door_lock.change(Locked)
    # time.sleep(5)
    # door_lock.change(Locked)

    user = User(door_lock, 'JohnDoe')
    user.authenticate()
    user.control_lock(Unlocked)
    # user.control_lock(Unlocked)
    user.control_lock(Locked)
    #
    # print('simulate login timeout')
    # time.sleep(31)
    #
    # user.control_lock(Unlocked)

    # door_lock.change(Unlocked)
    # door_lock.change(Locked)
    # door_lock.change(Unlocked)
    # door_lock.change(Locked)
    # door_lock.change(Locked)