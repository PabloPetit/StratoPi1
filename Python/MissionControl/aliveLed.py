from config import *
import RPi.GPIO as GPIO
from threading import Thread
import time

class LightThread(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global  bGreen, bBlue
        while True:
            GPIO.output(BLUE_LED, not GPIO.input(BLUE_LED))
            time.sleep(0.5)

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(BLUE_LED, GPIO.OUT)
GPIO.setup(LIFE_LINE_PIN, GPIO.OUT)
GPIO.output(LIFE_LINE_PIN, GPIO.HIGH)

t = LightThread()
t.start()
