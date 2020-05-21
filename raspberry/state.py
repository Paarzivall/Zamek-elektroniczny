# import RPi.GPIO as GPIO
import time

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(17, GPIO.OUT)
# GPIO.setup(21, GPIO.OUT)
# GPIO.setup(26, GPIO.OUT)


def SetAngle(angle):
    """
    Set angle of servo. If the angle is lower than 30 degrees, the LED color is changed to red, otherwise is set
    to green.

    :param angle: angle in degrees
    :type angle: int
    :return: None
    :rtype: None
    """
    offset = 20
    angle = angle + offset
    print(f"setting angle on servo: {angle}")
    if angle < 30:
        SetLED('red')
    else:
        SetLED('green')

#    pwm = GPIO.PWM(17, 50)
#    pwm.start(0)
#    duty = angle / 18 + 2
#    GPIO.output(17, True)
#    pwm.ChangeDutyCycle(duty)
#    time.sleep(0.5)
#    pwm.stop()


def SetLED(color):
    """
    Set LED color based on argument. Support only for red and green colors.

    :param color: define LED color
    :type color: str
    :return: None
    :rtype: None
    """
    if color == 'red':
        pass
 #       GPIO.output(21, GPIO.LOW)
 #       GPIO.output(26, GPIO.HIGH)
    if color == 'green':
        pass
#        GPIO.output(26, GPIO.LOW)
#        GPIO.output(21, GPIO.HIGH)


class LockState:
    """
    This class implement state design pattern for Lock.
    """
    name = "state"
    allowed = []

    def __init__(self, lock=None):
        """
        Init method for LockState.

        :param lock: lock instance
        :type lock: Lock
        """
        self.lock = lock
        if self.lock is not None:
            lock.events.append(self.__lock_log)

    def switch(self, state):
        """
        Switch state of the Lock to the new state.

        :param state: define state (Locked, Unlocked)
        :type state: LockState
        :return: None
        :rtype: None
        """
        if state.name in self.allowed:
            self.__class__ = state
        else:
            self.__lock_log(f'[LockState Log] Current: {self} => switching to {state.name} not possible.')

    @staticmethod
    def __lock_log(msg):
        """
        Method to print logs. If the message is type of string, msg is printed.

        :param msg: Message to print.
        :type msg: str
        :return: None
        :rtype: None
        """
        if isinstance(msg, str):
            print(msg)

    def __str__(self):
        return self.name


class Locked(LockState):
    """
    This class defines Locked state of Lock.
    """
    name = "locked"
    allowed = ['unlocked']
    servo_angle = 0


class Unlocked(LockState):
    """
    This class defines Unlocked state of Lock.
    """
    name = "unlocked"
    allowed = ['locked']
    servo_angle = 90


class Event(list):
    """
    Event class for mediator desing pattern.
    """
    def __call__(self, *args, **kwargs):
        for item in self:
            item(*args, **kwargs)


class LockStateInfo:
    """
    Class used for passing data to mediator with information about LockState event.
    """
    def __init__(self, who_change, lock_action):
        """
        Init method for LockStateInfo. The instance of the class is passed to Mediator.

        :param who_change: User who change state.
        :type who_change: str
        :param lock_action: State has been changed.
        :type lock_action: str
        """
        self.who_change_state = who_change
        self.lock_action = lock_action()
        self.lock_name = None


class UserAuthenticationInfo:
    """
    Class used for passing data to mediator with information about User Authentication event.
    """
    def __init__(self, who, success, level=''):
        """
        Init method for UserAuthenticationInfo. The instance of the class is passed to Mediator.

        :param who: User name.
        :type who: str
        :param success: Login status.
        :type success: bool
        :param level: Authentication level.
        :type level: str
        """
        self.who = who
        self.success = success
        self.level = level


class Lock:
    """
    A class representing a lock.
    This class is also a mediator which is calling events when Lock state is change or user tries to authenticate.
    """

    def __init__(self, name):
        """
        Init method of the lock.

        :param name: Defines name of the lock.
        :type name: str
        """
        self.name = name
        self.events = Event()
        self.state = Locked(self)
        self.allowed_users = []

    def change(self, state, args=None):
        """
        Change the lock state and calls Mediator events.

        :param state: define state which needs to be set.
        :type state: LockState
        :param args: Instance of LockStateInfo.
        :type args: LockStateInfo
        :return: None
        :rtype: None
        """
        self.state.switch(state)
        if args is not None:
            args.lock_name = self.name
            self.events(args)
        SetAngle(self.state.servo_angle)

    def authentication(self, args):
        """
        Calls Mediator events when user is authenticated.

        :param args: Contains information which user tries to log in and on which level.
        :type args: UserAuthenticationInfo
        :return: None
        :rtype: None
        """
        self.events(args)


class MasterLog:
    """
    Class used in mediator design pattern, MasterLog subscribes events from Lock.
    """
    def __init__(self, lock):
        """
        Init method for MasterLog.

        :param lock: Instance of log to which MasterLog need to be connected.
        :type lock: Lock
        """
        lock.events.append(self.save_log)
        self.state_logs = []
        self.auth_logs = []

    def save_log(self, args):
        """
        Method prints logs and saves them to proper attributes.

        :param args: Information which need to be printed and stored in state_logs or auth_logs.
        :type args: LockStateInfo or UserAuthenticationInfo
        :return: None
        :rtype: None
        """
        if isinstance(args, LockStateInfo):
            msg = f'[Master Log] State of lock: {args.lock_name} changed to: {args.lock_action} by: {args.who_change_state}'
            self.state_logs.append(msg)
            print(msg)
        elif isinstance(args, UserAuthenticationInfo):
            msg = f'[Authentication Log] User {args.who} tried to log in with success: {args.success}, ' \
                  f'auth-level: {args.level}'
            self.auth_logs.append(msg)
            print(msg)


