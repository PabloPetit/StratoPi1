from threading import *
from datetime import *
import time



class Module( Thread ):

    def __init__(self, fUpdateDelay):

        Thread.__init__( self )

        self.oLock = Lock()
        self.fDelay = fUpdateDelay
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
            time.sleep( self.fUpdateDelay )

    def evaluate_command_states(self):

            for oCom in self.dCommandStates.values():

                if oCom.IsOn :

                    tdTimeDelta = datetime.now() - oCom.dtLastCheck
                    fDeltaSeconds = tdTimeDelta.total_seconds()

                    if fDeltaSeconds > oCom.fTimeout:
                        oCom.funCommand()
                        oCom.dtLastCheck = datetime.now()


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



class CommandState():

    """
        This class represent a certain functional state of the module that must be frequently updated.
        An exemple would be : "Is able to send an sms" or "How much batterie is left"
        
        The CommandState consist of :
         
         - An evaluation function which will determine if the concerned functionality is operational
         - A timeout, which represent the validity time of an evanluation
         - The date of the last evaluation
         - The current state of the functionality as an integer. Zero must represent a non-functionnal state
         - A log function which returns a human-readable string for record purposes
         - A name (String)
         - A Is On boolean which tells if the state must be refreshed
         
         A module will, in its loop and for each of its CommandStates, check if the timeout is over
         and in this case, run the evaluation function to update the current state.
         
         The evaluation function should receive as first argument
         
         The CommandStates are stored in a dictionnary whose keys will be a string 
         
         
         Note : not happy with log method ... will not be implemented for now
    """

    def __init__(self, funCommand, fTimeout, sName = "Defaut Command"):
        self.funCommand = funCommand # Command that takes no arguments
        self.fTimeout = fTimeout #Timeout in seconds
        self.bOk = 0
        self.dtLastCheck = datetime.min
        self.sName = sName
        self.bIsOn = True

    def log(self): # Example :
        sLog = self.sName
        if self.bOk :
            sLog+= " is operational [ "+ str(self.bOk)+" ]"
        else:
            sLog += " is not operational [ " + str(self.bOk) + " ]"

        sLog += " Last Check : "+ str(self.dtLastCheck)





"""
    Probably useless
"""


class State:
    INITIALIZING = 5  # InitialState
    OPERATIONAL = 1  # Init done, functional test ok
    ASLEEP = 2  # Module Put to sleep waiting for awake
    NOT_RESPONDING = 3  # Module has not respond to last functional test
    RECONNECTING = 4
    DEAD = 5  # ... Mission failure