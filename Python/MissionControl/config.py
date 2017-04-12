import serial


sDefautl_port = '/dev/cu.usbserial-A503S1B9'
fDefault_timeout = 2000
fSleep_step = 50

# Sim800l configuration match serial.Serial() default configuration
iDefault_bauds = 115200
iDefault_byte_size = serial.EIGHTBITS
iDefault_parity = serial.PARITY_NONE
iDefual_stop_bits = serial.STOPBITS_ONE

cCtrlZ = '\x1a'