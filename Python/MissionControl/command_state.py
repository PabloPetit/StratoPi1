from datetime import *
from config import *


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
        self.dStates = {}
        self.create_dict_state()

    def create_dict_state(self):
        raise NotImplementedError("Create dict states not implemented")

    def log_str(self):
        sLog = "[ "+self.sName+" ]"
        sLog += " Last check : "+ str(self.dtLastCheck)
        sLog += " State [ " + self.dStates[self.iState][1]
        sLog += " , "+str(self.iState)+" ]"
        return sLog

    def set_state(self):
        pass


#  @@@@@@@@@@@@@@@@@@@@@@@@ AT STATE  @@@@@@@@@@@@@@@@@@@@@



class ATState(CommandState):

    def __init__(self, funCommand, fTimeout, sName):
        CommandState.__init__(self, funCommand, fTimeout, sName)

    def create_dict_state(self):
        self.dStates[0] = [0, "No Response"]
        self.dStates[1] = [1, "AT OK"]

    def log_str(self):
        return super(ATState, self).log_str()

#  @@@@@@@@@@@@@@@@@@@@@@@@ BATTERY STATE  @@@@@@@@@@@@@@@@@@@@@

class BatteryState(CommandState):


    def __init__(self, funCommand, fTimeout, sName):
        i=0
        CommandState.__init__(self, funCommand, fTimeout, sName)
        self.iVoltage = 0
        self.iPercent = 0

    def create_dict_state(self):
        self.dStates = {
        0 : [0,   "BATTERY_DEAD"],
        1 : [10,  "VERY_LOW_CHARGE"],
        2 : [25,  "LOW_CHARGE"],
        3 : [50,  "HALF_CHARGE"],
        4 : [75,  "HIGH_CHARGE"],
        5 : [95,  "FULL_CHARGE"]
    }

    def set_state(self):

        for k in self.dStates.keys():
            if self.iPercent <= self.dStates[k][0]:
                self.iState = k
                break

    def log_str(self):
        return super(BatteryState, self).log_str() + " : "+str(self.iPercent)+"% : "+str(self.iVoltage)+"mV"


#  @@@@@@@@@@@@@@@@@@@@@@@@ TEMPERATURE STATE  @@@@@@@@@@@@@@@@@@@@@

# Note that the sensor might be broken on the sim ... 23.73 degres is the only value I can get
class TemperatureState(CommandState):

    def __init__(self, funCommand, fTimeout, sName):
        CommandState.__init__(self, funCommand, fTimeout, sName)
        self.fDegres = -273.15

    def create_dict_state(self):

        self.dStates = {
            0: [-273.15, "ABSOLUT_ZERO"],
            1: [-40, "DANGEROUSLY_COLD"],
            2: [-20, "LOW_NEGATIVE"],
            3: [0, "NEGATIVE"],
            4: [7, "COLD"],
            5: [25, "OPTIMAL"],
            6: [30, "HOT"],
            7: [50, "DANGEROUSLY_HOT"]
        }

    def set_state(self):
        for k in self.dStates.keys():
            if self.fDegres <= self.dStates[k][0]:
                self.iState = k
                break

    def log_str(self):
        return super(TemperatureState, self).log_str() + " : " + str(self.fDegres) + "°C"

#  @@@@@@@@@@@@@@@@@@@@@@@@ SIGNAL STATE  @@@@@@@@@@@@@@@@@@@@@

class SignalState(CommandState):

    def __init__(self, funCommand, fTimeout, sName):
        CommandState.__init__(self, funCommand, fTimeout, sName)
        self.bConnected = False
        self.iStrenght = 0

    def create_dict_state(self):
        self.dStates = {
            0 : [0, "NO_SIGNAL"],
            1 : [5, "VERY_LOW_SIGNAL"],
            2 : [10, "LOW_SIGNAL"],
            3 : [15, "SIGNAL_OK"],
            4 : [20, "GOOD_SIGNAL"],
            5 : [30, "VERY_GOOD_SIGNAL"],
            6 : [31, "UNLIMITED_SIGNAL!"]
        }

    def set_state(self):

        if self.iStrenght == 99: # Special case, 99 means unknow signal or no signal
            self.iState = 0
            return

        for k in self.dStates.keys():
            if self.iStrenght <= self.dStates[k][0]:
                self.iState = k
                break

    def log_str(self):
        return super(SignalState, self).log_str() + " : " + str(self.iStrenght)


#  @@@@@@@@@@@@@@@@@@@@@@@@ SMS MODE STATE  @@@@@@@@@@@@@@@@@@@@@

class CMGFState(CommandState):
    # Associate with CMGF = 1
    def __init__(self, funCommand, fTimeout, sName):
        CommandState.__init__(self, funCommand, fTimeout, sName)
        self.iSmsMode = 0

    def create_dict_state(self):
        self.dStates[0] = [0, "SMS Mode : Cannot send messages"]
        self.dStates[1] = [1, "SMS Mode : Operational"]

    def set_state(self):
        self.iState = self.iSmsMode

    def log_str(self):
        return super(CMGFState, self).log_str()


#  @@@@@@@@@@@@@@@@@@@@@@@@ SMS MEMORY STATE  @@@@@@@@@@@@@@@@@@@@@





#  @@@@@@@@@@@@@@@@@@@@@@@@      ADC STATE    @@@@@@@@@@@@@@@@@@@@@


class ADCState(CommandState):
    # Associate with CMGF = 1
    def __init__(self, funCommand, fTimeout, sName):
        CommandState.__init__(self, funCommand, fTimeout, sName)
        self.iState = 1

        self.lTempBattery = [0, 0, 0]
        self.lTempOutside = [0, 0, 0]
        self.lUV = [0, 0]

    def create_dict_state(self):
        self.dStates[0] = [0, "Should Not Happen"]
        self.dStates[1] = [1, "Operational"]

    def log_str(self):
        sLog  = super(CMGFState, self).log_str()+"\n"
        sLog += "      UV : " +str(self.lUV[0])+", "+str(self.lUV[1])+"mV\n"
        sLog += "      Temp bat : " + str(self.lTempBattery[0]) + ", " + str(self.lTempBattery[1]) + "mV, "+str(self.lTempBattery[2]+" °C\n")
        sLog += "      Temp out : " + str(self.lTempOutside[0]) + ", " + str(self.lTempOutside[1]) + "mV, "+str(self.lTempOutside[2]+" °C\n")












