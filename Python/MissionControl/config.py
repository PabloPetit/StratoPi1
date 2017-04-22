import serial


DEFAULT_UART_PORT = '/dev/cu.usbserial-A503S1B9'
DEFAULT_UART_COMMAND_TIMEOUT = 1



# Sim800l configuration match serial.Serial() default configuration
DEFAULT_BAUDS = 115200
DEFAULT_BYTE_SIZE = serial.EIGHTBITS
DEFAULT_PARITY = serial.PARITY_NONE
DEFAULT_STOP_BITS = serial.STOPBITS_ONE

CTRL_Z = '\x1a'
B_NULL = b'\x00'



#@@@@@@@@@@@ REFRESH TIMERS @@@@@@@@@@@

# GSM MODULE :

# Could be a good idea to unsynchronized the timeouts to avoid heavy charge on same loop
# and thus long time with lock state - timers must be prime

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

