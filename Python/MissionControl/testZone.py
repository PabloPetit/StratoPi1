from gsm_module import *
from adc_module import *
from gps_module import *
import logging
import sys
import os

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


gsm = GsmModule(oLog, GSM_UART_PORT)
gsm.setup()
gsm.start()

gps = GPSModule(oLog, GPS_UART_PORT)
gps.setup()
gps.start()

adc = ADCModule(oLog)
adc.setup()
adc.start()