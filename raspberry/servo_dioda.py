import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

def SetLED(color):
    if color == 'red':
        GPIO.output(21, GPIO.LOW)
        GPIO.output(26, GPIO.HIGH)
    if color == 'green':
        GPIO.output(26, GPIO.LOW)
        GPIO.output(21, GPIO.HIGH)

def SetAngle(angle):
    offset = 20
    angle = angle + offset
    if angle < 30:
        SetLED('red')
    else:
        SetLED('green')

    pwm = GPIO.PWM(17, 50)
    pwm.start(0)
    duty = angle / 18 + 2
    GPIO.output(17, True)
    pwm.ChangeDutyCycle(duty)
    sleep(0.5)
    pwm.stop()

angles = [0, 90, 0, 90] * 5

try:
    for angle in angles:
        SetAngle(angle)
        sleep(3)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
