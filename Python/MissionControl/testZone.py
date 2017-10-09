print("Starting tests")


from config import *


from gps_module import *
from camera_module import *
from adc_module import *
from gsm_module import *

print("StartUp")
i = 0
while os.path.isdir(HOME_PATH):
    while HOME_PATH[len(HOME_PATH)].isdigit() or HOME_PATH[len(HOME_PATH)] == "/":
        HOME_PATH = HOME_PATH[:len(HOME_PATH) - 1]
        print( HOME_PATH)
    HOME_PATH += str(i) + "/"
    print(HOME_PATH)
    i+=1

print("Done")

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
GPIO.setup(LIFE_LINE_PIN, GPIO.OUT)

GPIO.output(LIFE_LINE_PIN, GPIO.HIGH)

if not os.path.isdir( MAIN_LOG_PATH  ):
    os.makedirs(MAIN_LOG_PATH )

if not os.path.isdir( CAMERA_CAPTURE_PATH  ):
    os.makedirs(CAMERA_CAPTURE_PATH )

if not os.path.isdir( CAMERA_VIDEO_PATH  ):
    os.makedirs(CAMERA_VIDEO_PATH )

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

for i in range(0,10):
    oMainLog.info("---------------\n")

oMainLog.info("--------   STARTING NEW INSTANCE   -------\n")

for i in range(0,10):
    oMainLog.info("---------------\n")


bGPS = True
bCam = False
bADC = False
bGSM = True

if bGPS:
    gps = GPSModule(oMainLog, GPS_UART_PORT)
    gps.setup()
    gps.start()

if bCam:
    Camera = CameraModule(oMainLog)
    Camera.setup()
    Camera.start()

if bADC:
    adc = ADCModule(oMainLog)
    adc.setup()
    adc.start()

if bGSM:
    gsm = GsmModule(oMainLog, GSM_UART_PORT)
    gsm.setup()
    gsm.start()




