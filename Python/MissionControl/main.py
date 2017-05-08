from gsm_module import *
from adc_module import *
from gps_module import *
from config import *
import logging
import os
import RPi.GPIO as GPIO


# GPIO and Led controller Initialization

#Creation of logger and handlers


# Modules and their PeridicalChecks should be stored in a common dictionnary to allow clean acces to them
# Periodical check should have lock to allow thread safe reading and writing

# Creation of Modules

# Module Starting

# Wait for Module initialiazion

# Send

oDebugHandler = None
oInfoHandler = None
oWarningHandler = None
oMainLog = None

dModules = {}
dMainPeriodicalChecks = {}


def create_main_log():
    if not os.path.isdir(MAIN_LOG_PATH):
        os.makedirs(MAIN_LOG_PATH)

    global oDebugHandler, oInfoHandler, oWarningHandler, oMainLog

    oDebugHandler = logging.handlers.TimedRotatingFileHandler(MAIN_LOG_PATH + DEBUG_LOG_PATH, when="m",
                                                              interval=LOG_FILE_ROTATION_MINUTES,
                                                              encoding="utf-8")

    oInfoHandler = logging.handlers.TimedRotatingFileHandler(MAIN_LOG_PATH + INFO_LOG_PATH, when="m",
                                                             interval=LOG_FILE_ROTATION_MINUTES,
                                                             encoding="utf-8")

    oWarningHandler = logging.handlers.TimedRotatingFileHandler(MAIN_LOG_PATH + WARNING_LOG_PATH, when="m",
                                                                interval=LOG_FILE_ROTATION_MINUTES,
                                                                encoding="utf-8")

    oDebugHandler.setFormatter(LOG_FORMATTER)
    oInfoHandler.setFormatter(LOG_FORMATTER)
    oWarningHandler.setFormatter(LOG_FORMATTER)

    oDebugHandler.setLevel(logging.DEBUG)
    oInfoHandler.setLevel(logging.INFO)
    oWarningHandler.setLevel(logging.WARNING)

    oMainLog = logging.getLogger("MainLogger")
    oMainLog.setLevel(logging.DEBUG)  # Acceptes everthings, filter done with handlers
    oMainLog.addHandler(oDebugHandler)
    oMainLog.addHandler(oInfoHandler)
    oMainLog.addHandler(oWarningHandler)


def setup_GPIO():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)
    GPIO.setup(BUTTON, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(BLUE_LED, GPIO.OUT)
    GPIO.setup(GREEN_LED, GPIO.OUT)

    GPIO.output(BLUE_LED, GPIO.LOW)
    GPIO.output(GREEN_LED, GPIO.LOW)


def create_modules():
    global oDebugHandler, oInfoHandler, oWarningHandler, oMainLog, dModules, dMainPeriodicalChecks

    Gsm = GsmModule(oMainLog, GSM_UART_PORT)
    dModules[GSM_NAME] = Gsm


def send_confirmation_sms():
    pass

def start_recording():
    pass

def end_flight():
    pass



