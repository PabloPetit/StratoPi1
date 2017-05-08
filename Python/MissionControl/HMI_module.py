from module import *
import RPi.GPIO as GPIO

class HMIModule(Module):

    def __init__(self, oMainLog):
        Module.__init__(self, oMainLog)

        self.name = HMI_NAME
        self.sLogPath = HMI_LOG_PATH
        self.fUpdateDelay = HMI_UPDATE_DELAY
        self.tMainLogInterval = DEFAULT_MAIN_LOG_INTERVAL

        self.bButtonState = True

    def setup(self):
        super(HMIModule, self).setup()

    def create_periodical_checks(self):
        pass

    def send_raw_log(self):
        pass

    def module_run(self):

        if GPIO.input(BUTTON) != self.bButtonState:
            self.info("Button pressed")



    def check_self_integrity(self):
        return True

    def handle_no_integrity(self):
        pass

    def send_log(self, bForwardMain):
        pass