from datetime import datetime, timedelta
import logging
import logging.handlers
import serial

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ GLOBAL VARIABLES @@@@@@@@@@@@@@@@@@@@@@@@@@@

oDebugHandler = None
oInfoHandler = None
oWarningHandler = None
oMainLog = None

dModules = {}
dMainPeriodicalChecks = {}

bConfirmSMSReceived = False
bEndMission = False

dtSysStartTime = datetime.now()
dtFirstGPSTime = datetime.min



#@@@@@@@@@@@@@@ MISSION CONTROL RELATED @@@@@@@@@@


WAIT_FOR_STARTUP_SLEEP = 5
WAIT_FOR_CONFIRMATION_SMS_SLEEP = 5
WAIT_FOR_MISSION_LAUNCH_SLEEP = 0.05

CONFIRMATION_BLINK_INTERVAL = 0.5
CONFIRMATION_BLINK_TIME = timedelta(seconds=10)

FLIGHT_LOOP_SLEEP = 5
MINIMAL_LOCATION_SMS_SENT = 10


#@@@@@@@@@@@@@@ PRINTER RELATED @@@@@@@@@@@@


LOG_FILE_ROTATION_MINUTES = 45#30
DEFAULT_MAIN_LOG_INTERVAL = timedelta(minutes = 3)
HOME_PATH = "/home/pi/Documents/MissionData/"
#HOME_PATH = "/Users/Pablo/Documents/MissionData/"

LOG_FORMATTER = logging.Formatter("[ %(name)s - %(levelname)s ] %(asctime)s - %(message)s")
RAW_LOG_FORMATTER = logging.Formatter("[ RAW ] %(asctime)s --- \n%(message)s")
ONLY_MESSAGE_LOG_FORMATTER = logging.Formatter("%(message)s")

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
GPS_UPDATE_DELAY = 0.8
CAMERA_UPDATE_DELAY = 0 # This NEEDS to be 0, sleep is then re-implemented in the camera_module

ACQUIRE_TIMEOUT = 35 # F
JOIN_TIMEOUT = 30

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

LIFE_LINE_PIN = 11 # IMPORTANT : Life line is set to HIGH in Main.setup_GPIO()

GREEN_LED = 16
BLUE_LED = 13
BUTTON = 18

GSM_RESET_PIN = 40

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

UTC_OFFSET = 2

GPS_MEMORY = 40

GPS_BUFFER_READ_INTERVAL = 0.025
GPS_MAX_WAIT_TIME = 2

GPRMC = "GPRMC"
GPVTG = "GPVTG"
GPGGA = "GPGGA"
GPGLL = "GPGLL"
GPGSA = "GPGSA"
GPGSV = "GPGSV"

#@@@@@@@@@@@@@@ UART RELATED @@@@@@@@@@@@@@@@

GSM_UART_PORT = '/dev/ttyUSB0'
GPS_UART_PORT = '/dev/serial0'
#GPS_UART_PORT = '/dev/tty.usbserial-A503S1B9'

DEFAULT_UART_PORT = '/dev/serial0'
DEFAULT_UART_COMMAND_TIMEOUT = 1

DEFAULT_BAUDS = 115200
GPS_BAUDS = 9600
DEFAULT_BYTE_SIZE = serial.EIGHTBITS
DEFAULT_PARITY = serial.PARITY_NONE
DEFAULT_STOP_BITS = serial.STOPBITS_ONE

CTRL_Z = '\x1a'
B_NULL = b'\x00'
B_XFF = b'\xff'

#@@@@@@@@@@@ CAMERA @@@@@@@@@@@@@@@@@@@@@@@@


MAIN_DISK_PATH = "/dev/root"

CAMERA_CAPTURE_FILE_NAME_FORMAT = '{timestamp:%H%M%S}-{counter:003d}.png'

CAMERA_LOW_ALTITUDE_LIMIT = 15000




#@@@@@@@@@@@@@@@@@@@@@@@ PLUG INFO @@@@@@@@@@@@@@@@@@@
"""

USB UART FTDI HEADER :

1 RTS Ready to Send
2 RXD Receive
3 TXD Transmit
4 CTS Clear to Send
5 GND Ground
6 SYS3V3 Power Supply (3.3V) 


MCP3008 connexions : 

MCP3008 VDD to Raspberry Pi 3.3V
MCP3008 VREF to Raspberry Pi 3.3V
MCP3008 AGND to Raspberry Pi GND
MCP3008 DGND to Raspberry Pi GND
MCP3008 CLK to Raspberry Pi SCLK = PIN 23 [ BLUE ]
MCP3008 DOUT to Raspberry Pi MISO = PIN 21 [ GREEN ]
MCP3008 DIN to Raspberry Pi MOSI = PIN 19 [ YELLOW ]
MCP3008 CS/SHDN to Raspberry Pi CE0 = PIN 24 [ ORANGE ]


"""













