import serial
import logging
import datetime

#@@@@@@@@@@@@@@ PRINTER RELATED @@@@@@@@@@@@


LOG_FILE_ROTATION_MINUTES = 5#30

DEFAULT_MAIN_LOG_INTERVAL = datetime.timedelta(minutes = 5)

LOG_FORMATTER = logging.Formatter("[ %(name)s - %(levelname)s ] %(asctime)s - %(message)s")

#HOME_PATH = "/home/pi/Documents/MissionData/"
HOME_PATH = "/Users/Pablo/Desktop/MissionData/"

DEFAULT_NAME = "ModuleName"

GSM_NAME = "GSM"
ADC_NAME = "ADC"
CAMERA_NAME = "Camera"
GPS_NAME = "GPS"

GSM_LOG_PATH = HOME_PATH + GSM_NAME + '/'
ADC_LOG_PATH = HOME_PATH + ADC_NAME + '/'
CAMERA_LOG_PATH = HOME_PATH + CAMERA_NAME + '/'
GPS_LOG_PATH = HOME_PATH + GPS_NAME + '/'

DEBUG_LOG_PATH = "Debug/"
INFO_LOG_PATH = "Info/"

#@@@@@@@@@@@@@@ UART RELATED @@@@@@@@@@@@@@@@

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

#Debug :
BATTERY_REFRESH_TIMEOUT = 1
TEMPERATURE_REFRESH_TIMEOUT = 1
SIGNAL_REFRESH_TIMEOUT = 1
AT_REFRESH_TIMEOUT = 1
SMS_REFRESH_TIMEOUT = 1
CMGF_REFRESH_TIMEOUT = 1

"""
BATTERY_REFRESH_TIMEOUT = 120
TEMPERATURE_REFRESH_TIMEOUT = 120
SIGNAL_REFRESH_TIMEOUT = 120
AT_REFRESH_TIMEOUT = 120
SMS_REFRESH_TIMEOUT = 120
CMGF_REFRESH_TIMEOUT = 1
"""

#@@@@@@@@@@@@@@ SMS STUFF @@@@@@@@@@@@@@

MAX_SMS_LENGHT = 140
DEFAULT_MAX_TRY_TIME = datetime.timedelta( minutes = 5 )





















