print("Starting tests")


from config import *


from gps_module import *
from camera_module import *
from adc_module import *


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

bGPS = False
bCam = True
bADC = False

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




