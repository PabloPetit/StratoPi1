from threading import *
from queue import *
from datetime import *
from config import *
from command_state import *
import time



class Module( Thread ):

    def __init__(self, fUpdateDelay):

        Thread.__init__( self )

        self.oLock = Lock()
        self.fUpdateDelay = fUpdateDelay
        self.bStop = False # Use to force a module shutdown
        self.dCommandStates = {}
        self.create_command_states()
        self.name = "Default Module Name"

    def create_command_states(self):
        raise NotImplementedError("create_command_states not implemented")

    def run(self):

        while not self.stop_condition():

            self.evaluate_command_states()

            if not self.check_self_integrity():
                self.handle_no_integrity()
            else:
                self.module_run()
                self.log()

            # May be useful to check how much time last the current iteration and wait in consequence
            time.sleep( self.fUpdateDelay )

    def evaluate_command_states(self):

            for oCom in self.dCommandStates.values():

                if oCom.bIsOn:

                    tdTimeDelta = datetime.now() - oCom.dtLastCheck
                    fDeltaSeconds = tdTimeDelta.total_seconds()

                    if fDeltaSeconds > oCom.fTimeout:
                        oCom.funCommand()
                        oCom.dtLastCheck = datetime.now()
                        oCom.log()



    def stop_condition(self):
        return self.bStop

    def check_self_integrity(self):
        raise NotImplementedError("check_self_integrity not implemented")

    def handle_no_integrity(self):
        raise NotImplementedError("handle_no_integrity not implemented")

    def module_run(self):
        raise NotImplementedError("module_run not implemented")

    def log(self):
        raise NotImplementedError("log not implemented")






