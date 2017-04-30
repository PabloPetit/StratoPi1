from threading import *
from queue import *
from datetime import *
from config import *
from command_state import *
import logging
import logging.handlers
import time
import sys
import os

# All import are done here to allow single import in derived classes


class Module( Thread ):

    def __init__(self, oMainLog):

        Thread.__init__( self)
        self.bStop = False # Use to force a module shutdown
        self.dCommandStates = {}
        self.create_command_states()
        self.dtLastMainLogDate = datetime.min
        self.oLog = None
        self.oMainLog = oMainLog
        self.oDebugHandler = None
        self.oInfoHandler= None

        # ATTRIBUTS TO REDEFINE

        self.name = DEFAULT_NAME
        self.sLogPath = HOME_PATH + __name__
        self.fUpdateDelay = MODULE_DEFAULT_UPDATE_DELAY
        self.tMainLogInterval = DEFAULT_MAIN_LOG_INTERVAL
         #Don't forget to call setup_logger in derived classes


    def setup(self):
        self.setup_logger()


    def setup_logger(self):

        if not os.path.isdir(self.sLogPath):
            os.makedirs(self.sLogPath)

        self.oDebugHandler = logging.handlers.TimedRotatingFileHandler(self.sLogPath + DEBUG_LOG_PATH, when="m",
                                                                       interval=LOG_FILE_ROTATION_MINUTES,
                                                                       encoding="utf-8")

        self.oInfoHandler = logging.handlers.TimedRotatingFileHandler(self.sLogPath + INFO_LOG_PATH, when="m",
                                                                       interval=LOG_FILE_ROTATION_MINUTES,
                                                                       encoding="utf-8")

        self.oDebugHandler.setFormatter(LOG_FORMATTER)
        self.oInfoHandler.setFormatter(LOG_FORMATTER)

        self.oDebugHandler.setLevel(logging.DEBUG)
        self.oInfoHandler.setLevel(logging.INFO)

        self.oLog = logging.getLogger(self.name)
        self.oLog.setLevel(logging.DEBUG) # Acceptes everthings, filter done with handlers
        self.oLog.addHandler(self.oDebugHandler)
        self.oLog.addHandler(self.oInfoHandler)


    def create_command_states(self):
        raise NotImplementedError("create_command_states not implemented")

    def run(self):
        self.info("Run Started", True)
        while not self.stop_condition():
            self.debug("Begin Loop")
            self.evaluate_command_states()

            if not self.check_self_integrity():
                self.error("Integrity check not passed")
                self.handle_no_integrity()
            else:
                self.debug("Integrity check passed")
                self.module_run()
                if datetime.now() - self.dtLastMainLogDate > self.tMainLogInterval :
                    self.send_log(True)
                    self.dtLastMainLogDate = datetime.now()

            time.sleep( self.fUpdateDelay )
        self.warning("Run Ended")

    def evaluate_command_states(self):
        self.debug("Checking CommandStates ...")
        for oCom in self.dCommandStates.values():
            if oCom.bIsOn:
                tdTimeDelta = datetime.now() - oCom.dtLastCheck
                fDeltaSeconds = tdTimeDelta.total_seconds()

                if fDeltaSeconds > oCom.fTimeout:
                    oCom.funCommand()
                    oCom.set_state()
                    oCom.dtLastCheck = datetime.now()
        self.debug("Checking CommandStates Done")



    def stop_condition(self):
        return self.bStop

    def check_self_integrity(self):
        raise NotImplementedError("check_self_integrity not implemented")

    def handle_no_integrity(self):
        raise NotImplementedError("handle_no_integrity not implemented")

    def module_run(self):
        raise NotImplementedError("module_run not implemented")


# @@@@@@@@@@@@@@@ LOG FUNCTIONS @@@@@@@@@@@@@@@@@@@@@@@@

    def send_log(self, bForwardMain):
        sLog = "  --[ "+self.name+" CURRENT STATE ]---\n"
        for oCom in self.dCommandStates.values():
            sLog+="        "+oCom.log_str()+"\n"
        self.info(sLog,True)

    def debug(self, sMessage, bForwardMain = False):
        self.oLog.debug(sMessage)
        if bForwardMain:
            self.oMainLog.debug(sMessage)

    def info(self, sMessage, bForwardMain = False):
        self.oLog.info(sMessage)
        if bForwardMain:
            self.oMainLog.info(sMessage)

    def warning(self, sMessage, bForwardMain = True):
        self.oLog.warning(sMessage)
        if bForwardMain:
            self.oMainLog.warning(sMessage)

    def error(self, sMessage, bForwardMain = True):
        self.oLog.error(sMessage)
        if bForwardMain:
            self.oMainLog.error(sMessage)

    def critical(self, sMessage, bForwardMain = True):
        self.oLog.critical(sMessage)
        if bForwardMain:
            self.oMainLog.critical(sMessage)


    def exception(self, sMessage, bForwardMain = True):
        self.oLog.exception(sMessage)
        if bForwardMain:
            self.oMainLog.exception(sMessage)




