from uart_module import *


"""
    Remeber to aquire and realease Lock before and after each command that communicates on the Serial

"""


BATTERY_STATE = "battery"
TEMPERATURE_STATE = "temperature"
SIGNAL_STATE = "signal"
SMS_STATE = "sms"
AT_STATE = "at"


class GsmModule( UartModule ):

    def __init__(self, fUpdateDelay):
        UartModule.__init__(self, fUpdateDelay)
        self.name = "GSM_Module"

        # It is probably better to use a queue for the sms as they take some time to send
        # It will avoid to lock threads that need to send sms for too long
        self.qSms_to_send = Queue()

        # This dictionnary contains the possible request a user can send via sms, and the associated function
        # For instance, if the module receives a sms with the word STATE, it will respond by sending the global state of the probe
        self.dSms_commands = {
            "STATE" : self.send_state
        }

        self.dTelephone_numbers = {
            "PABLO" : "0645160520",
            "DOUDOU" : "0645224118",
            "ROBIN" : "0646773226",
            "THIBAULT" : "0781856866"
        }

    def create_command_states(self):
        self.dCommandStates[AT_STATE] = ATState(self.at_check, AT_REFRESH_TIMEOUT, AT_STATE)
        self.dCommandStates[BATTERY_STATE] = BatteryState(self.check_battery, BATTERY_REFRESH_TIMEOUT, BATTERY_STATE)
        self.dCommandStates[TEMPERATURE_STATE] = TemperatureState(self.check_temperature, TEMPERATURE_REFRESH_TIMEOUT, TEMPERATURE_STATE)
        self.dCommandStates[SIGNAL_STATE] = SignalState(self.check_signal_strenght, SIGNAL_REFRESH_TIMEOUT, SIGNAL_STATE)



# @@@@@@@@@@@@@@@@@@@@@@@@ MODULE FUNCTIONS @@@@@@@@@@@@@@@@@@@

    def check_self_integrity(self):
        return True

    def handle_no_integrity(self):
        pass

    def module_run(self):

        self.manage_sms_queue()
        self.manage_sms_reception()

    def log(self):
        pass

# @@@@@@@@@@@@@@@@@@@@@@@@ REGION @@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def manage_sms_reception( self ):
        pass


    def manage_sms_queue(self):

        if  self.qSms_to_send.empty():
            return

        oSms = self.qSms_to_send.get()


    #The following
    def _send_sms(self, lSms):# list [ string, list [string] ]
        pass

# @@@@@@@@@@@@@@@@@@@@@@@@@ USER COMMANDS @@@@@@@@@@@@@@@@@@@@@@@@@@@

    def send_sms( self, sMessage, lNumbers):

        if len(lNumbers) < 1 or len(sMessage) > MAX_SMS_LENGHT:
            return False

        self.qSms_to_send.put([sMessage, lNumbers])
        return True

    def disable_communication(self):
        self.oLock.acquire()

        self.oLock.release()

    def enable_communication(self):
        self.oLock.acquire()

        self.oLock.release()


    def hard_reset(self):
        #Reset the module the hard way by pulling down the reset cicuit
        self.oLock.acquire()

        self.oLock.release()

    def clear_sms_memory(self, bOnlyAlreadyRedMessages = True):
        self.oLock.acquire()

        self.oLock.release()



# @@@@@@@@@@@@@@@@@@@@@@@ SMS COMMANDS @@@@@@@@@@@@@@@@@@@@@@@@@

    def send_state( self ): # send sms with location, batterie charge, temperature ...
        self.oLock.acquire()

        self.oLock.release()


# @@@@@@@@@@@@@@@@@@@@@@ COMMAND STATES @@@@@@@@@@@@@@@@@@@@@@@@


    def check_battery(self):
        self.oLock.acquire()
        self.send_command("AT+CBC", {"+CBC:": self.read_battery_charge})
        self.oLock.release()


    def check_temperature(self ):
        self.oLock.acquire()
        self.send_command("AT+CMTE?", {"+CMTE:": self.read_temperature}, 2) # Takes some time to get a response
        self.oLock.release()


    def check_signal_strenght(self):
        self.oLock.acquire()
        self.send_command("AT+CSQ", {"+CSQ:": self.read_signal_strength}, 2)
        self.oLock.release()



# @@@@@@@@@@@@@@@@@@@@@@@@ RESPONSE FUNCTIONS @@@@@@@@@@@@@@@@@@@@@

    """
        Response function have to take the response string as an argument, to avoid TypeError exception
    """

    #Response type : +CBC: 0,85,4087
    def read_battery_charge(self, sResponse):
        try:
            values = sResponse.split()[1]
            values = values.split(',') # [0, 85, 4087]
            batteryState = self.dCommandStates[BATTERY_STATE]
            batteryState.iPercent = int(values[1]) # 85
            batteryState.iVoltage = int(values[2]) # 4087
            print("Battery : " +str(batteryState.iPercent)+ "% - "+str(batteryState.iVoltage)+"mV")
        except Exception:
            pass #TODO do something

    #Response type : +CMTE: 0,23.73
    def read_temperature(self, sResponse):
        try:
            values = sResponse.split()[1] # "0, 23.73 "
            values = values.split(',') # [ 0, 23.73 ]
            tempState = self.dCommandStates[TEMPERATURE_STATE]
            tempState.fDegres = float(values[1]) # 23.73
            print("Temperature : "+str(tempState.fDegres))
        except Exception:
            pass

    # Response type : +CSQ: 15,0
    def read_signal_strength(self, sResponse):
        try:
            values = sResponse.split()[1]
            values = values.split(',')
            signalState = self.dCommandStates[SIGNAL_STATE]
            signalState.iStrenght = int(values[0])
            print("Signal : "+str(signalState.iStrenght))
        except Exception:
            pass



#@@@@@@@@@@@@@@@@@@@@@@@@@@ COMMAND STATES @@@@@@@@@@@@@@@@@@@@@@@



class BatteryState(CommandState):

    VERY_LOW_CHARGE = 10
    LOW_CHARGE = 25
    HALF_CHARGE = 50
    HIGH_CHARGE = 75
    FULL_CHARGE = 95

    def __init__(self, funCommand, fTimeout, sName):
        i=0
        CommandState.__init__(self, funCommand, fTimeout, sName)
        self.iVoltage = 0
        self.iPercent = 0

# Note that the sensor might be broken on the sim ... 23.73 degres is the only value I can get
class TemperatureState(CommandState):

    def __init__(self, funCommand, fTimeout, sName):
        CommandState.__init__(self, funCommand, fTimeout, sName)
        self.sName = "GSM_Temperature_State"
        self.fDegres = -273.15

class SignalState(CommandState):

    NO_SIGNAL = 99
    LOW_SIGNAL = 0
    MAX_SIGNAL = 31

    def __init__(self, funCommand, fTimeout, sName):
        CommandState.__init__(self, funCommand, fTimeout, sName)
        self.bConnected = False
        self.iStrenght = 0
