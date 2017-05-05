import serial
import logging
from datetime import *

#@@@@@@@@@@@@@@ PRINTER RELATED @@@@@@@@@@@@


LOG_FILE_ROTATION_MINUTES = 15#30

DEFAULT_MAIN_LOG_INTERVAL = timedelta(minutes = 3)

LOG_FORMATTER = logging.Formatter("[ %(name)s - %(levelname)s ] %(asctime)s - %(message)s")
RAW_LOG_FORMATTER = logging.Formatter("%(asctime)s --- %(message)s")

HOME_PATH = "/home/pi/Documents/MissionData/"
#HOME_PATH = "/Users/Pablo/Desktop/MissionData/"

DEFAULT_NAME = "ModuleName"

RAW_NAME = "_RAW"

MAIN_LOG_NAME = "Main"
GSM_NAME = "GSM"
ADC_NAME = "ADC"
CAMERA_NAME = "Camera"
GPS_NAME = "GPS"

GSM_LOG_PATH = HOME_PATH + GSM_NAME + '/'
ADC_LOG_PATH = HOME_PATH + ADC_NAME + '/'
CAMERA_LOG_PATH = HOME_PATH + CAMERA_NAME + '/'
GPS_LOG_PATH = HOME_PATH + GPS_NAME + '/'
MAIN_LOG_PATH = HOME_PATH + MAIN_LOG_NAME + '/'

DEBUG_LOG_PATH = "debug.log"
INFO_LOG_PATH = "info.log"
WARNING_LOG_PATH = "warning.log"
RAW_LOG_PATH = "raw.log"

#@@@@@@@@@@@@@@ UART RELATED @@@@@@@@@@@@@@@@

GSM_UART_PORT = '/dev/ttyUSB0'
GPS_UART_PORT = '/dev/serial0'

DEFAULT_UART_PORT = '/dev/cu.usbserial-A503S1B9'
DEFAULT_UART_COMMAND_TIMEOUT = 1

# Sim800l configuration match serial.Serial() default configuration
DEFAULT_BAUDS = 115200
DEFAULT_BYTE_SIZE = serial.EIGHTBITS
DEFAULT_PARITY = serial.PARITY_NONE
DEFAULT_STOP_BITS = serial.STOPBITS_ONE

CTRL_Z = '\x1a'
B_NULL = b'\x00'

#@@@@@@@@@@@ MODULE RELATED  @@@@@@@@@@@@@@@@

MODULE_DEFAULT_UPDATE_DELAY = 5

GSM_UPDATE_DELAY = 2
ADC_UPDATE_DELAY = 2
GPS_UPDATE_DELAY = 2
CAMERA_UPDATE_DELAY = 3


#@@@@@@@@@@@ COMMAND STATE REFRESH @@@@@@@@@@@

# GSM MODULE :

GSM_HARD_RESET_DELAY = timedelta(minutes=3)


#Debug :
BATTERY_REFRESH_TIMEOUT = 1
TEMPERATURE_REFRESH_TIMEOUT = 1
SIGNAL_REFRESH_TIMEOUT = 1
AT_REFRESH_TIMEOUT = 1
SMS_REFRESH_TIMEOUT = 1
CMGF_REFRESH_TIMEOUT = 1
ADC_REFRESH_TIMEOUT = 1

"""
BATTERY_REFRESH_TIMEOUT = 120
TEMPERATURE_REFRESH_TIMEOUT = 120
SIGNAL_REFRESH_TIMEOUT = 120
AT_REFRESH_TIMEOUT = 120
SMS_REFRESH_TIMEOUT = 120
CMGF_REFRESH_TIMEOUT = 1
"""

#@@@@@@@@@@@@@@ SMS RELATED @@@@@@@@@@@@@@

MAX_SMS_LENGHT = 140
DEFAULT_MAX_TRY_TIME = timedelta( minutes = 5 )



# @@@@@@@@@@@@@@@@@@@@@@ ADC AND GPIO RELATED @@@@@@@@@@@@@@@@

SPICLK = 23
SPIMISO = 21
SPIMOSI = 19
SPICS = 24

GSM_RESET_PIN = 42


TEMP_BATTERY_ADC_PIN = 0
TEMP_OUTSIDE_ADC_PIN = 1
UV_ADC_PIN = 7


# @@@@@@@@@@@@@@@@@@@@@@@@ COMMAND STATES @@@@@@@@@@@@@@@@@@@@@

BATTERY_STATE = "battery"
TEMPERATURE_STATE = "temperature"
SIGNAL_STATE = "signal"
SMS_STATE = "sms"
CMGF_STATE = "cmgf"
AT_STATE = "at"
ADC_STATE = "adc"


# @@@@@@@@@@@@@@@@@@@@@@@@ GPS RELATED @@@@@@@@@@@@@@@@


GPS_MEMORY = 40

GPRMC = "GPRMC"
GPVTG = "GPVTG"
GPGGA = "GPGGA"
GPGLL = "GPGLL"
GPGSA = "GPGSA"
GPGSV = "GPGSV"











