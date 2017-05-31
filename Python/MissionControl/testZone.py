print("Starting tests")


from config import *
import RPi.GPIO as GPIO

from gps_module import *
from camera_module import *

bGreen, bBlue = False, False

class LightThread(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global  bGreen, bBlue
        while True:
            if bGreen:
                GPIO.output(GREEN_LED, not GPIO.input(GREEN_LED))
            else:
                GPIO.output(GREEN_LED, GPIO.LOW)

            if bBlue:
                GPIO.output(BLUE_LED, not GPIO.input(BLUE_LED))
            else:
                GPIO.output(BLUE_LED, GPIO.LOW)
            time.sleep(0.5)

if not os.path.isdir( MAIN_LOG_PATH  ):
    os.makedirs(MAIN_LOG_PATH )

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

oLog = logging.getLogger("MainLogger")
oLog.setLevel(logging.DEBUG)  # Acceptes everthings, filter done with handlers
oLog.addHandler(oDebugHandler)
oLog.addHandler(oInfoHandler)
oLog.addHandler(oWarningHandler)

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(BUTTON, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(BLUE_LED, GPIO.OUT)
GPIO.setup(GREEN_LED, GPIO.OUT)

GPIO.output(BLUE_LED, GPIO.LOW)
GPIO.output(GREEN_LED, GPIO.LOW)

t = LightThread()
t.start()

bBlue = True
"""
gsm = GsmModule(oLog, GSM_UART_PORT)
gsm.setup()
gsm.start()
"""

while GPIO.input(BUTTON):

    time.sleep(WAIT_FOR_MISSION_LAUNCH_SLEEP)
bGreen = True

gps = GPSModule(oLog, GPS_UART_PORT)
gps.setup()
gps.start()


print("Green on")
"""
Camera = CameraModule(oMainLog)
Camera.setup()
Camera.start()
"""
"""
adc = ADCModule(oLog)
adc.setup()
adc.start()
"""




