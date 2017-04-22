from datetime import *


BATTERY_STATE = "battery"
TEMPERATURE_STATE = "temperature"
SIGNAL_STATE = "signal"
SMS_STATE = "sms"
CMGF_STATE = "cmgf"
AT_STATE = "at"



class CommandState():

    """
        This class represent a certain functional state of the module that must be frequently updated.
        An exemple would be : "Is able to send an sms" or "How much batterie is left"

        The CommandState consist of :

         - An evaluation functions list which will determine if the concerned functionality is operational
         - A timeout, which represent the validity time of an evanluation
         - The date of the last evaluation
         - The current state of the functionality as an integer. Zero must represent a non-functionnal state
         - A set_state function which update the state from the last referesh
         - A log function which returns a human-readable string for record purposes
         - A name (String)

         A module will, in its loop and for each of its CommandStates, check if the timeout is over
         and in this case, run the evaluation function to update the current state.

         The evaluation function should receive as first argument

         The CommandStates are stored in a dictionnary whose keys will be a string 


         Note : not happy with log method ... will not be implemented for now
    """

    def __init__(self, funCommand, fTimeout, sName = "Defaut_Command_Name"):
        i = 0
        self.funCommand = funCommand # Command that takes no arguments
        self.fTimeout = fTimeout  # Timeout in seconds
        self.iState = 0
        self.dtLastCheck = datetime.min
        self.sName = sName
        self.bIsOn = True

    def log(self): # Example :
        sLog = self.sName
        if self.iState > 0 : sLog+= " is operational [ "+ str(self. iState)+" ]"
        else:
            sLog += " is not operational [ " + str(self.iState) + " ]"

        sLog += " Last Check : "+ str(self. dtLastCheck)

    def set_state(self):
        pass


#  @@@@@@@@@@@@@@@@@@@@@@@@ AT STATE  @@@@@@@@@@@@@@@@@@@@@



class ATState(CommandState):

    def __init__(self, funCommand, fTimeout, sName):
        CommandState.__init__(self, funCommand, fTimeout, sName)

    #No set_state, already done in funCommand

#  @@@@@@@@@@@@@@@@@@@@@@@@ BATTERY STATE  @@@@@@@@@@@@@@@@@@@@@

class BatteryState(CommandState):


    BATTERY_PERCENT_STATES = {
        0 : [0,   "BATTERY_DEAD" ],
        1 : [10,  "VERY_LOW_CHARGE" ],
        2 : [25,  "LOW_CHARGE" ],
        3 : [50,  "HALF_CHARGE" ],
        4 : [75,  "HIGH_CHARGE" ],
        5 : [95,  "FULL_CHARGE" ]
    }

    def __init__(self, funCommand, fTimeout, sName):
        i=0
        CommandState.__init__(self, funCommand, fTimeout, sName)
        self.iVoltage = 0
        self.iPercent = 0

    def set_state(self):

        for k in BatteryState.BATTERY_PERCENT_STATES.keys():
            if self.iPercent <= BatteryState.BATTERY_PERCENT_STATES[k]:
                self.iState = k
                break


#  @@@@@@@@@@@@@@@@@@@@@@@@ TEMPERATURE STATE  @@@@@@@@@@@@@@@@@@@@@

# Note that the sensor might be broken on the sim ... 23.73 degres is the only value I can get
class TemperatureState(CommandState):

    TEMP_STATES = {
        0 : [-273.15, "ABSOLUT_ZERO" ], # HA
        1 : [-40,     "DANGEROUSLY_COLD" ],
        2 : [-20,     "LOW_NEGATIVE" ],
        3 : [0,       "NEGATIVE" ],
        4 : [7,       "COLD" ],
        5 : [25 ,     "OPTIMAL" ],
        6 : [30,      "HOT" ],
        7 : [50,      "DANGEROUSLY_HOT" ]
    }

    def __init__(self, funCommand, fTimeout, sName):
        CommandState.__init__(self, funCommand, fTimeout, sName)
        self.sName = "GSM_Temperature_State"
        self.fDegres = -273.15

    def set_state(self):
        for k in BatteryState.BATTERY_PERCENT_STATES.keys():
            if self.fDegres <= TemperatureState.TEMP_STATES[k]:
                self.iState = k
                break

#  @@@@@@@@@@@@@@@@@@@@@@@@ SIGNAL STATE  @@@@@@@@@@@@@@@@@@@@@

class SignalState(CommandState):

    SIGNAL_STATES = {
        0 : [0, "NO_SIGNAL"],
        1 : [5, "VERY_LOW_SIGNAL"],
        2 : [10, "LOW_SIGNAL"],
        3 : [15, "SIGNAL_OK"],
        4 : [20, "GOOD_SIGNAL"],
        5 : [30, "VERY_GOOD_SIGNAL"],
        6 : [31, "UNLIMITED_SIGNAL!"]
    }

    def __init__(self, funCommand, fTimeout, sName):
        CommandState.__init__(self, funCommand, fTimeout, sName)
        self.bConnected = False
        self.iStrenght = 0

    def set_state(self):

        if self.iStrenght == 99: # Special case, 99 means unknow signal or no signal
            self.iState = 0
            return

        for k in SignalState.SIGNAL_STATES.keys():
            if self.fDegres <= SignalState.SIGNAL_STATES[k]:
                self.iState = k
                break


#  @@@@@@@@@@@@@@@@@@@@@@@@ SMS MODE STATE  @@@@@@@@@@@@@@@@@@@@@

class CMGFState(CommandState):
    # Associate with CMGF = 1
    def __init__(self, funCommand, fTimeout, sName):
        CommandState.__init__(self, funCommand, fTimeout, sName)
        self.iSmsMode = 0

    def set_state(self):
        self.iState = self.iSmsMode


#  @@@@@@@@@@@@@@@@@@@@@@@@ SMS MEMORY STATE  @@@@@@@@@@@@@@@@@@@@@


class SmsMemoryState(CommandState):

    def __init__(self, funCommand, fTimeout, sName):
        CommandState.__init__(self, funCommand, fTimeout, sName)


    def set_state(self):
        pass















