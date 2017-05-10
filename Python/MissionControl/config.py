import serial
import logging
from datetime import *
from camera_module import CameraSetting

#@@@@@@@@@@@@@@ PRINTER RELATED @@@@@@@@@@@@


LOG_FILE_ROTATION_MINUTES = 15#30
DEFAULT_MAIN_LOG_INTERVAL = timedelta(minutes = 3)
HOME_PATH = "/home/pi/Documents/MissionData/"

LOG_FORMATTER = logging.Formatter("[ %(name)s - %(levelname)s ] %(asctime)s - %(message)s")
RAW_LOG_FORMATTER = logging.Formatter("%(asctime)s --- %(message)s")

DEFAULT_NAME = "ModuleName"
RAW_NAME = "_RAW"
MAIN_LOG_NAME = "Main"
GSM_NAME = "GSM"
ADC_NAME = "ADC"
CAMERA_NAME = "Camera"
GPS_NAME = "GPS"
HMI_NAME = "HMI"

GSM_LOG_PATH = HOME_PATH + GSM_NAME + '/'
ADC_LOG_PATH = HOME_PATH + ADC_NAME + '/'
CAMERA_LOG_PATH = HOME_PATH + CAMERA_NAME + '/'
GPS_LOG_PATH = HOME_PATH + GPS_NAME + '/'
HMI_LOG_PATH = HOME_PATH + HMI_NAME + '/'
MAIN_LOG_PATH = HOME_PATH + MAIN_LOG_NAME + '/'

DEBUG_LOG_PATH = "debug.log"
INFO_LOG_PATH = "info.log"
WARNING_LOG_PATH = "warning.log"
RAW_LOG_PATH = "raw.log"

CAMERA_CAPTURE_PATH = CAMERA_LOG_PATH+"Captures/"
CAMERA_VIDEO_PATH = CAMERA_LOG_PATH+"Videos/"

#@@@@@@@@@@@@@@ SMS AND GSM RELATED @@@@@@@@@@@@@@

READY_MINIMAL_SIGNAL = 5
MAX_SMS_LENGHT = 140
DEFAULT_MAX_TRY_TIME = timedelta( minutes = 5 )

GSM_RESET_HIGH_LEVEL_TIME = 0.3

dTelephone_numbers = {
            "PABLO" : "0645160520",
            "DOUDOU" : "0645224118",
            "ROBIN" : "0646773226",
            "THIBAULT" : "0781856866"
        }


#@@@@@@@@@@@ MODULE RELATED  @@@@@@@@@@@@@@@@

MODULE_DEFAULT_UPDATE_DELAY = 5

GSM_UPDATE_DELAY = 2
ADC_UPDATE_DELAY = 2
GPS_UPDATE_DELAY = 2
CAMERA_UPDATE_DELAY = 3
HMI_UPDATE_DELAY = 0.1

ACQUIRE_TIMEOUT = 35 # F

#@@@@@@@@@@@ COMMAND STATE REFRESH @@@@@@@@@@@

# GSM MODULE :

GSM_HARD_RESET_DELAY = timedelta(minutes=3)

BATTERY_REFRESH_TIMEOUT = 1
TEMPERATURE_REFRESH_TIMEOUT = 1
SIGNAL_REFRESH_TIMEOUT = 1
AT_REFRESH_TIMEOUT = 1
SMS_REFRESH_TIMEOUT = 1
CMGF_REFRESH_TIMEOUT = 1
ADC_REFRESH_TIMEOUT = 1
MEMORY_REFRESH_TIMEOUT = 1

# @@@@@@@@@@@@@@@@@@@@@@ ADC AND GPIO RELATED @@@@@@@@@@@@@@@@

# GPIO
SPICLK = 23
SPIMISO = 21
SPIMOSI = 19
SPICS = 24

GREEN_LED = 16
BLUE_LED = 13
BUTTON = 18

GSM_RESET_PIN = 42

# MCP3008

TEMP_BATTERY_ADC_PIN = 0
TEMP_OUTSIDE_ADC_PIN = 1
UV_ADC_PIN = 7


# @@@@@@@@@@@@@@@@@@@@@@@@ PERIODICAL CHECKS @@@@@@@@@@@@@@@@@@@@@

BATTERY_STATE = "battery"
TEMPERATURE_STATE = "temperature"
SIGNAL_STATE = "signal"
SMS_STATE = "sms"
CMGF_STATE = "cmgf"
AT_STATE = "at"
ADC_STATE = "adc"
MEMORY_STATE = "memory"


# @@@@@@@@@@@@@@@@@@@@@@@@ GPS RELATED @@@@@@@@@@@@@@@@


GPS_MEMORY = 40

GPRMC = "GPRMC"
GPVTG = "GPVTG"
GPGGA = "GPGGA"
GPGLL = "GPGLL"
GPGSA = "GPGSA"
GPGSV = "GPGSV"

#@@@@@@@@@@@@@@ UART RELATED @@@@@@@@@@@@@@@@

GSM_UART_PORT = '/dev/ttyUSB0'
GPS_UART_PORT = '/dev/serial0'

DEFAULT_UART_PORT = '/dev/serial0'
DEFAULT_UART_COMMAND_TIMEOUT = 1

DEFAULT_BAUDS = 115200
DEFAULT_BYTE_SIZE = serial.EIGHTBITS
DEFAULT_PARITY = serial.PARITY_NONE
DEFAULT_STOP_BITS = serial.STOPBITS_ONE

CTRL_Z = '\x1a'
B_NULL = b'\x00'


#@@@@@@@@@@@ CAMERA @@@@@@@@@@@@@@@@@@@@@@@@


MAIN_DISK_PATH = "/dev/root"

CAMERA_CAPTURE_FILE_NAME_FORMAT = '{timestamp:%H%M%S}-{counter:003d}.png'

CAMERA_LOW_ALTITUDE_LIMIT = 15000


CAMERA_MAX_SETTING = CameraSetting(
                lCaptureResolution=(3280, 2464),
                lVideoResolution=(1920, 1080),
                iFPS=30,
                iCaptureQuality = 100,
                iVideoQuality=10,
                bRecordVideo=True,
                bRecordCapture=True,
                tCaptureInterval=timedelta(seconds=30),
                tVideoDuration=timedelta(minutes=15)
            )

CAMERA_HIGH_SETTING = CameraSetting(
                lCaptureResolution=(3280, 2464),
                lVideoResolution=(1920, 1080),
                iFPS=24,
                iCaptureQuality = 100,
                iVideoQuality=20,
                bRecordVideo=True,
                bRecordCapture=True,
                tCaptureInterval=timedelta(seconds=30),
                tVideoDuration=timedelta(minutes=15)
            )

CAMERA_MEDUIM_SETTING = CameraSetting(
                lCaptureResolution=(3280, 2464),
                lVideoResolution=(1280, 720),
                iFPS=24,
                iCaptureQuality = 100,
                iVideoQuality=20,
                bRecordVideo=True,
                bRecordCapture=True,
                tCaptureInterval=timedelta(seconds=45),
                tVideoDuration=timedelta(minutes=10)
            )

CAMERA_LOW_SETTING = CameraSetting(
                lCaptureResolution=(3280, 2464),
                lVideoResolution=(1280, 720),
                iFPS=24,
                iCaptureQuality = 100,
                iVideoQuality=20,
                bRecordVideo=False,
                bRecordCapture=True,
                tCaptureInterval=timedelta(seconds=60),
                tVideoDuration=timedelta(minutes=10)
            )















