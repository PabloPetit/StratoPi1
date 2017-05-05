from threading import *
from queue import *
from datetime import *
from config import *
from periodical_check import *
import logging
import logging.handlers
import time
import sys
import os


class Module( Thread ):

    def __init__(self, oMainLog):

        Thread.__init__( self)
        self.bStop = False # Use to force a module shutdown
        self.dPeriodicalChecks = {}
        self.create_peridical_checks()
        self.dtInitDate = datetime.now()
        self.dtLastMainLogDate = datetime.min
        self.oLog = None
        self.oRawLog = None
        self.oMainLog = oMainLog
        self.oDebugHandler = None
        self.oInfoHandler= None
        self.oRawHandler = None

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

        self.oRawHandler = logging.handlers.TimedRotatingFileHandler(self.sLogPath + RAW_LOG_PATH, when="m",
                                                                      interval=LOG_FILE_ROTATION_MINUTES,
                                                                      encoding="utf-8")

        self.oDebugHandler.setFormatter(LOG_FORMATTER)
        self.oInfoHandler.setFormatter(LOG_FORMATTER)
        self.oRawHandler.setFormatter(RAW_LOG_FORMATTER)

        self.oDebugHandler.setLevel(logging.DEBUG)
        self.oInfoHandler.setLevel(logging.INFO)
        self.oRawHandler.setLevel(logging.DEBUG)

        self.oLog = logging.getLogger(self.name)
        self.oLog.setLevel(logging.DEBUG) # Acceptes everthings, filter done with handlers
        self.oRawLog = logging.getLogger(self.name+RAW_NAME)

        self.oLog.addHandler(self.oDebugHandler)
        self.oLog.addHandler(self.oInfoHandler)
        self.oRawLog.addHandler(self.oRawHandler)


    def create_peridical_checks(self):
        raise NotImplementedError("create_command_states not implemented")

    def run(self):
        self.info("Run Started", True)
        while not self.stop_condition():
            self.debug("Begin Loop")
            self.evaluate_periodical_checks()

            if not self.check_self_integrity():
                self.error("Integrity check not passed")
                self.handle_no_integrity()
            else:
                self.debug("Integrity check passed")
                self.module_run()
                if datetime.now() - self.dtLastMainLogDate > self.tMainLogInterval :
                    self.send_log(True)
                    self.dtLastMainLogDate = datetime.now()
                else:
                    self.send_log(False)
                self.send_raw_log()

            time.sleep( self.fUpdateDelay )
        self.warning("Run Finished")

    def evaluate_periodical_checks(self):
        self.debug("Evaluating Periodical Checks ...")
        for oCom in self.dPeriodicalChecks.values():
            if oCom.bIsOn:
                tdTimeDelta = datetime.now() - oCom.dtLastCheck
                fDeltaSeconds = tdTimeDelta.total_seconds()

                if fDeltaSeconds > oCom.fTimeout:
                    oCom.funCommand()
                    oCom.set_state()
                    oCom.dtLastCheck = datetime.now()
        self.debug("Evaluating Periodical Checks Done")



    def stop_condition(self):
        return self.bStop

    def check_self_integrity(self):
        raise NotImplementedError("check_self_integrity not implemented")

    def handle_no_integrity(self):
        raise NotImplementedError("handle_no_integrity not implemented")

    def module_run(self):
        raise NotImplementedError("module_run not implemented")


# @@@@@@@@@@@@@@@ LOG FUNCTIONS @@@@@@@@@@@@@@@@@@@@@@@@

    def send_raw_log(self):
        raise NotImplementedError("Send raw should be redifined")

    def send_log(self, bForwardMain):
        sLog = "  --[ "+self.name+" CURRENT STATE ]---\n"
        for oCom in self.dPeriodicalChecks.values():
            sLog+="        "+oCom.log_str()+"\n"
        self.info(sLog,bForwardMain)

    def debug(self, sMessage, bForwardMain = False):
        self.oLog.debug(sMessage)
        if bForwardMain:
            self.oMainLog.debug(" [ "+self.name+" ] "+sMessage)

    def info(self, sMessage, bForwardMain = False):
        self.oLog.info(sMessage)
        if bForwardMain:
            self.oMainLog.info(" [ " + self.name + " ] " + sMessage)

    def warning(self, sMessage, bForwardMain = True):
        self.oLog.warning(sMessage)
        if bForwardMain:
            self.oMainLog.warning(" [ " + self.name + " ] " + sMessage)

    def error(self, sMessage, bForwardMain = True):
        self.oLog.error(sMessage)
        if bForwardMain:
            self.oMainLog.error(" [ " + self.name + " ] " + sMessage)

    def critical(self, sMessage, bForwardMain = True):
        self.oLog.critical(sMessage)
        if bForwardMain:
            self.oMainLog.critical(" [ " + self.name + " ] " + sMessage)


    def exception(self, sMessage, bForwardMain = True):
        self.oLog.exception(sMessage)
        if bForwardMain:
            self.oMainLog.exception(" [ " + self.name + " ] " + sMessage)




