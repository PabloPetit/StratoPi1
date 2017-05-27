from datetime import *
import logging
import logging.handlers

import time
import os
import sys
import serial

import subprocess
from threading import *
from queue import *

import collections

from picamera import *
import RPi.GPIO as GPIO

from config import *
from periodical_check import *
from module import *
from uart_module import *

from gsm_module import *
from adc_module import *
from gps_module import *
from camera_module import *



#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ GLOABAL VARIABLES @@@@@@@@@@@@@@@@@@@@@@@@@@@

oDebugHandler = None
oInfoHandler = None
oWarningHandler = None
oMainLog = None

dModules = {}
dMainPeriodicalChecks = {}

bConfirmSMSReceived = False
bEndMission = False

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ FUNCTIONS @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

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
    oMainLog.info("Logging ready")


def setup_GPIO():
    global oMainLog
    oMainLog.info("Begin of GPIO setup")
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)
    GPIO.setup(BUTTON, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(BLUE_LED, GPIO.OUT)
    GPIO.setup(GREEN_LED, GPIO.OUT)
    GPIO.setup(GSM_RESET_PIN, GPIO.OUT)

    GPIO.output(BLUE_LED, GPIO.HIGH)
    GPIO.output(GREEN_LED, GPIO.LOW)
    GPIO.output(GSM_RESET_PIN, GPIO.LOW)
    oMainLog.info("GPIO setup done")


def create_modules():
    global  oMainLog

    oMainLog.info("Creating Modules ...")

    GSM = GsmModule(oMainLog, GSM_UART_PORT)
    oMainLog.info("GSM created")

    GPS = GPSModule(oMainLog, GPS_UART_PORT)
    oMainLog.info("GPS created")

    Camera = CameraModule(oMainLog)
    oMainLog.info("Camera created")
    ADC = ADCModule(oMainLog)

    oMainLog.info("ADC created")
    oMainLog.info("Launching Module Setups ...")

    GSM.setup()
    oMainLog.info("GSM is up")

    GPS.setup()
    oMainLog.info("GPS is up")

    Camera.setup()
    oMainLog.info("Camera is up")

    ADC.setup()
    oMainLog.info("ADC is up")

    oMainLog.info("All setups done")
    oMainLog.info("Starting all Modules but Camera")

    GSM.start()
    oMainLog.info("GSM is running")

    GPS.start()
    oMainLog.info("GPS is running")

    ADC.start()
    oMainLog.info("ADC is running")
    oMainLog.info("All Modules running")


def wait_for_module_start_up():
    global dModules, oMainLog
    bAllOk = False
    oMainLog.info("Waiting for modules to start-up..")
    while not bAllOk:
        bAllOk = True
        for mod in dModules:
            if not mod.bIsReady:
                bAllOk = False
                oMainLog.info(mod.name+" is not yet ready")
            else:
                oMainLog.info(mod.name + " is ready")

        time.sleep(WAIT_FOR_STARTUP_SLEEP)

    oMainLog("All Modules ready")


def send_confirmation_sms():
    global dModules, oMainLog, dTelephone_numbers, bConfirmSMSReceived
    oMainLog.info("Sending sms for network confirmation request")
    oGSM = dModules[GSM_NAME]
    oSms = SmsToSend("Please send network confirmation sms with the performative : CONFIRM", list(dTelephone_numbers.values()))
    oGSM.qSms_to_send.put(oSms)

    while not bConfirmSMSReceived:
        oMainLog.info("Waiting for confirmation ...")
        time.sleep(WAIT_FOR_CONFIRMATION_SMS_SLEEP)

    oMainLog.info("Confirmation received")


def wait_for_mission_launch():
    global oMainLog
    oMainLog.info("Waiting for mission launch ...")
    GPIO.output(GREEN_LED, GPIO.HIGH)
    oMainLog("Green Led is on")

    while GPIO.input(BUTTON):
        time.sleep(WAIT_FOR_MISSION_LAUNCH_SLEEP)

    oMainLog.info("Mission launch order received")

def start_recording():
    global dModules, oMainLog
    oMainLog.info("Starting Camera Record")
    oCam = dModules[CAMERA_NAME]
    oCam.start()

    #  WAIT FOR CAMERA TO BE READY

    oMainLog.info("Camera is recording")

def confirmation_blink():
    global oMainLog
    oMainLog.info("Starting confirmation blink sequence")
    dtStart = datetime.now()
    bStop = False
    while not bStop:
        tElapsedTime = CONFIRMATION_BLINK_TIME - (datetime.now() - dtStart)
        bStop = tElapsedTime.days < 0
        GPIO.output(BLUE_LED, not GPIO.input(BLUE_LED))
        GPIO.output(GREEN_LED, not GPIO.input(GREEN_LED))
        time.sleep(CONFIRMATION_BLINK_INTERVAL)

    GPIO.output(BLUE_LED, GPIO.LOW)
    GPIO.output(GREEN_LED, GPIO.LOW)
    oMainLog.info("Leds off")
    oMainLog.info("Confirmation blink sequence finished")
    oMainLog.info("Ready for flight")


def flight_loop():
    global dModules, oMainLog, dMainPeriodicalChecks
    oSignalState = dMainPeriodicalChecks[SIGNAL_STATE]

    bHasTouchDown = False
    bButtonReadLoopActivated = False
    iLocationSMSsSent = 0


    while not bEndMission and iLocationSMSsSent < MINIMAL_LOCATION_SMS_SENT:

        if not GPIO.input(BUTTON):#Button pressed
            pass

        time.sleep(FLIGHT_LOOP_SLEEP)


def wait_for_end_mission():
    pass

def end_mission():
    global dModules, oMainLog
    oMainLog.info("End of mission")
    oMainLog.info("Shutting down modules")

    for mod in dModules:
        oMainLog.info("Stopping "+mod.name)
        mod.stop_module()
        mod.join(JOIN_TIMEOUT)
        oMainLog.info(mod.name+" stopped")

    # TODO led signal, GPIO cleanup()

    oMainLog.info("Mission Finished, ready for final shutdown")

def shutdown():
    oMainLog.info("Shutdown")
    oMainLog.shutdown()
    #subprocesses.call("sudo shutdown"# )
    exit()

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#                                SCRIPT ZONE
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@



"""
    CREATE AN ABORT SYSTEM WITH AN SMS ?
"""

"""
create_main_log()

setup_GPIO()

create_modules()

wait_for_module_start_up()

send_confirmation_sms()

wait_for_mission_launch()

start_recording()

confirmation_blink()

flight_loop()

wait_for_end_mission()

end_mission()

shutdown()

"""





