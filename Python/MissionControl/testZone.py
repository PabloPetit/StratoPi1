from gsm_module import *
import logging

oDebugHandler = logging.handlers.TimedRotatingFileHandler(HOME_PATH + DEBUG_LOG_PATH, when="m",
                                                               interval=LOG_FILE_ROTATION_MINUTES,
                                                               encoding="utf-8")

oInfoHandler = logging.handlers.TimedRotatingFileHandler(HOME_PATH + INFO_LOG_PATH, when="m",
                                                              interval=LOG_FILE_ROTATION_MINUTES,
                                                              encoding="utf-8")

oDebugHandler.setFormatter(LOG_FORMATTER)
oInfoHandler.setFormatter(LOG_FORMATTER)

oDebugHandler.setLevel(logging.DEBUG)
oInfoHandler.setLevel(logging.INFO)

oLog = logging.getLogger("MainLogger")
oLog.setLevel(logging.DEBUG)  # Acceptes everthings, filter done with handlers
oLog.addHandler(oDebugHandler)
oLog.addHandler(oInfoHandler)


gsm = GsmModule(oLog)

gsm.start()


