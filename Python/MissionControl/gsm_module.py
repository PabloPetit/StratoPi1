from uart_module import *


class GsmModule( UartModule ):

    def __init__(self, fUpdateDelay):
        UartModule.__init__(self, fUpdateDelay)
        self.name = "GSM_Module"

        self.qSms_to_send = Queue()

        self.lSmsReceived = []

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

        self.sCurrentSmsMessage = ""
        self.iCurrentSmsState = 0

        self.set_CMGF_state()
        self.close_net_light()


    def create_command_states(self):
        self.dCommandStates[AT_STATE] = ATState(self.at_check, AT_REFRESH_TIMEOUT, AT_STATE)
        self.dCommandStates[BATTERY_STATE] = BatteryState(self.check_battery, BATTERY_REFRESH_TIMEOUT, BATTERY_STATE)
        self.dCommandStates[TEMPERATURE_STATE] = TemperatureState(self.check_temperature, TEMPERATURE_REFRESH_TIMEOUT, TEMPERATURE_STATE)
        self.dCommandStates[SIGNAL_STATE] = SignalState(self.check_signal_strenght, SIGNAL_REFRESH_TIMEOUT, SIGNAL_STATE)
        self.dCommandStates[CMGF_STATE] = CMGFState(self.set_CMGF_state, CMGF_REFRESH_TIMEOUT, CMGF_STATE)

    def create_debuffer_dict(self):
        #self.dDebuffer_dict[str(B_NULL)] = "GSM_IS_DEAD"
        #self.dDebuffer_dict[] = "GSM_IS_DEAD"
        pass


# @@@@@@@@@@@@@@@@@@@@@@@@ MODULE FUNCTIONS @@@@@@@@@@@@@@@@@@@

    def check_self_integrity(self):
        return self.dCommandStates[AT_STATE].iState > 0

    def handle_no_integrity(self):
        pass

    def module_run(self):

        self.manage_sms_queue()
        self.manage_sms_reception()

    def log(self):
        pass


# @@@@@@@@@@@@@@@@@@@@@@@ COMMANDS @@@@@@@@@@@@@@@@@@@@@@@@@


    def set_CMGF_state(self):
        self.send_command("AT+CMGF=1", {"OK": self.read_cmgf, "ERROR" : self.read_cmgf})

    def close_net_light(self):
        self.send_command("AT+CNETLIGHT=0", {"OK": self.read_netlight, "ERROR" : self.read_netlight})


# @@@@@@@@@@@@@@@@@@@@@@@@ SMS RECEPTION @@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    # AT+CMGD=1 removes already read messages

    def manage_sms_reception(self):
        self.send_command("AT+CMGL=\"REC UNREAD\"", {"+CMGL:": self.read_sms}, 5)


    # +CMGL: 14,"REC UNREAD","+33645160520","","17/04/22,12:22:12+08"\r\nSTARTMESS AAAA A  \nAA ENDMESS\r\n\r\n
    def read_sms(self, sResponse):

        sResponse = sResponse[6:] # Removes "+CMGL: "
        (lInfos, sMessage) = sResponse.split("\r\n")
        lInfos = lInfos.split(',')
        iMemIndex = int(lInfos[0])
        sSender = lInfos[2]
        sDate =  lInfos[4]
        oSms = SmsReceived(sMessage,iMemIndex, sSender, sDate)

        self.lSmsReceived.append(oSms)
        self.switch_sms_message(oSms)

    def switch_sms_message(self, oSms):
        sPrefixe = oSms.sMessage.split(" ")[0]
        for com in self.dSms_commands.keys():
            if com.lower() == sPrefixe.lower():
                self.dSms_commands[com](oSms)
                break


    def check_memory_overload(self):
        pass




# @@@@@@@@@@@@@@@@@@@@@@@@ SMS SENDING @@@@@@@@@@@@@@@@@@@@@@@@@@@@@



    def manage_sms_queue(self):

        if  self.qSms_to_send.empty():
            return

        oSms = self.qSms_to_send.get()

        for n in oSms.lNumbers:
            self.send_sms(oSms.sMessage, n)


    def send_sms(self, sMessage, sNumber):
        self.sCurrentSmsMessage = sMessage
        sCom = "AT+CMGS=\""+sNumber+"\""
        self.send_command(sCom, {">" : self.write_sms}, "ERROR")

    def write_sms(self):
        pass

    # @@@@@@@@@@@@@@@@@@@@@@@ SMS COMMANDS @@@@@@@@@@@@@@@@@@@@@@@@@

    """
        Sms commands must receive the concerned sms
    """

    def send_state( self, oSms ): # send sms with location, batterie charge, temperature ...

        oBatteryState = self.dCommandStates[BATTERY_STATE]
        oSignalState = self.dCommandStates[SIGNAL_STATE]
        oTempState = self.dCommandStates[TEMPERATURE_STATE]
        sMessage = "BATTERY : "+str(oBatteryState.iPercent)+"% "+str(oBatteryState.iVoltage)+"mV\n"
        sMessage += "SIGNAL : "+str(oSignalState.iStrenght)+"\n"
        sMessage +=" TEMP : "+str(oTempState.fDegres)+"\n"
        oSmsToSend = SmsToSend(sMessage, [oSms.sSender])
        self.qSms_to_send.put(oSmsToSend)


# @@@@@@@@@@@@@@@@@@@@@@ COMMAND STATES @@@@@@@@@@@@@@@@@@@@@@@@


    def check_battery(self):
        self.send_command("AT+CBC", {"+CBC:": self.read_battery_charge})


    def check_temperature(self ):
        self.send_command("AT+CMTE?", {"+CMTE:": self.read_temperature}, 2) # Takes some time to get a response


    def check_signal_strenght(self):
        self.send_command("AT+CSQ", {"+CSQ:": self.read_signal_strength}, 2)



# @@@@@@@@@@@@@@@@@@@@@@@@ RESPONSE FUNCTIONS @@@@@@@@@@@@@@@@@@@@@

    """
        Response function have to take the response string as an argument, to avoid TypeError exception
        Also, do not forget to set the iState Value at the end of the function
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
            self.dCommandStates[BATTERY_STATE].iState = -1


    #Response type : +CMTE: 0,23.73
    def read_temperature(self, sResponse):
        try:
            values = sResponse.split()[1] # "0, 23.73 "
            values = values.split(',') # [ 0, 23.73 ]
            tempState = self.dCommandStates[TEMPERATURE_STATE]
            tempState.fDegres = float(values[1]) # 23.73
            print("Temperature : "+str(tempState.fDegres))
        except Exception:
            self.dCommandStates[TEMPERATURE_STATE].iState = -1

    # Response type : +CSQ: 15,0
    def read_signal_strength(self, sResponse):
        try:
            values = sResponse.split()[1]
            values = values.split(',')
            signalState = self.dCommandStates[SIGNAL_STATE]
            signalState.iStrenght = int(values[0])
            print("Signal : "+str(signalState.iStrenght))
        except Exception:
            self.dCommandStates[SIGNAL_STATE].iState = -1

    # Response type = OK or ERROR
    def read_cmgf(self, sResponse):

        CMGFState = self.dCommandStates[CMGF_STATE]
        CMGFState.iSmsMode = 0
        try:
            value = sResponse.split()[1]
            if value == "OK":
                CMGFState.iSmsMode = 1
        except Exception:
            pass


    # Response type = OK or ERROR
    def read_netlight(self, sResponse):
        try:
            value = sResponse.split()[1]
            if value == "OK":
                pass
        except Exception:
            pass


class SmsToSend():

    def __init__(self, sMessage, lNumbers, iPriority = 0 ):
        self.sMessage = sMessage # The message
        self.lNumbers = lNumbers # List of telephone numbers
        self.iPriority = iPriority # Not sure if it will be used
        self.dtCreationDate = datetime.now()
        self.dtLastSendTry = datetime.min




class SmsReceived():

    def __init__(self, sMessage, iMemIndex, sSender, sDate):
        self.sMessage = sMessage
        self.iMemIndex = iMemIndex
        self.sSender = sSender
        self.sDateReceivedSMS = sDate # String format
        self.dtDateReceivedModule = datetime.now()