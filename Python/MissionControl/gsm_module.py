from uart_module import *


class GsmModule( UartModule ):

    def __init__(self, oMainLog):
        UartModule.__init__(self, oMainLog)

        self.name = GSM_NAME
        self.sLogPath = GSM_LOG_PATH
        self.fUpdateDelay = GSM_UPDATE_DELAY

        self.qSms_to_send = Queue()
        self.lSmsReceived = []

        self.dSms_commands = {
            "STATE" : self.send_state,
            "REG" : self.register_numbers
            #"END_MISSION" : self.end_mission
        }

        self.dTelephone_numbers = {
            "PABLO" : "0645160520",
            "DOUDOU" : "0645224118",
            "ROBIN" : "0646773226",
            "THIBAULT" : "0781856866"
        }

        self.oCurrentSmsMessage = None



    def setup(self):
        super(GsmModule, self).setup()
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
        try:
            sResponse = sResponse[6:] # Removes "+CMGL: "
            (lInfos, sMessage) = sResponse.split("\r\n")
            lInfos = lInfos.split(',')
            iMemIndex = int(lInfos[0])
            sSender = lInfos[2]
            sDate =  lInfos[4]
            oSms = SmsReceived(sMessage, iMemIndex, sSender, sDate)

            self.info("Message received : \n"+oSms.log_str(), True)

            self.lSmsReceived.append(oSms)
            self.switch_sms_message(oSms)

        except Exception:
            self.exception("An error occured while reading an SMS : \n")

    def switch_sms_message(self, oSms):
        try:
            sPrefixe = oSms.sMessage.split(" ")[0]
            self.debug("Finding SMS prefixe : "+sPrefixe)
            for com in self.dSms_commands.keys():
                if com.lower() == sPrefixe.lower():
                    self.dSms_commands[com](oSms)
                    self.debug("Prefix found")
                    return
            self.warning("Prefix not found")
        except Exception:
            self.exception("An error occured while switching on SMS prefix : \n")


    def check_memory_overload(self):
        pass


# @@@@@@@@@@@@@@@@@@@@@@@@ SMS SENDING @@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    def manage_sms_queue(self):
        self.debug("Managing sms queue")
        if  self.qSms_to_send.empty():
            return

        oSms = self.qSms_to_send.get()

        for n in oSms.lNumbers:
            self.send_sms(oSms, n)


    def send_sms(self, oSms, sNumber):
        self.oCurrentSmsMessage = oSms
        self.oCurrentSmsMessage.dtLastSendTry = datetime.now()
        sCom = "AT+CMGS=\""+sNumber+"\""
        self.send_command(sCom, {'>' : self.write_sms, "ERROR" : self.sms_send_error})

    def write_sms(self, sResponse):
        try:
            self.debug("Writing sms")
            sMes = self.oCurrentSmsMessage.sMessage + CTRL_Z
            self.send_command(sMes, {'+CMGS:': self.sms_send_success, "ERROR": self.sms_send_error}, 10)
        except Exception:
            self.exception("An error occured while writing an SMS : \n")

    def sms_send_success(self, sResponse):
        self.info("SMS successfully sent : \n" + self.oCurrentSmsMessage.log_str())
        self.oCurrentSmsMessage.iSendState = SmsToSend.SMS_SEND_SUCCESS
        self.oCurrentSmsMessage = None

    def sms_send_error(self, sResponse):
        self.warning("Could not send SMS : \n" + self.oCurrentSmsMessage.log_str())
        self.oCurrentSmsMessage.iSendState = SmsToSend.SMS_SEND_FAILED

        if datetime.now() - self.oCurrentSmsMessage.dtLastSendTry > self.oCurrentSmsMessage :
            self.warning("Sending aborted")
        else:
            self.warning("SMS sent back to queue for retry")
            self.qSms_to_send.put(self.oCurrentSmsMessage)

        self.oCurrentSmsMessage = None



    # @@@@@@@@@@@@@@@@@@@@@@@ SMS COMMANDS @@@@@@@@@@@@@@@@@@@@@@@@@

    """
        Sms commands must receive the concerned sms
    """

    def send_state( self, oSms ): # send sms with location, batterie charge, temperature ...
        try:
            oBatteryState = self.dCommandStates[BATTERY_STATE]
            oSignalState = self.dCommandStates[SIGNAL_STATE]
            oTempState = self.dCommandStates[TEMPERATURE_STATE]
            sMessage = "BATTERY : "+str(oBatteryState.iPercent)+"% "+str(oBatteryState.iVoltage)+"mV\n"
            sMessage += "SIGNAL : "+str(oSignalState.iStrenght)+"\n"
            sMessage +="TEMP : "+str(oTempState.fDegres)+"\n"
            lNumberList = [ oSms.sSender.replace('"', "")]
            oSmsToSend = SmsToSend(sMessage, lNumberList)
            self.qSms_to_send.put(oSmsToSend)
            self.info("Sending STATE response to : "+str(lNumberList)+" Content : \n"+oSmsToSend.log_str())
        except Exception:
            self.exception("An error occured while trying to send current state : \n")

    def register_numbers(self, oSms):
        #Register the numbers in the sms
        #send ACK
        pass


# @@@@@@@@@@@@@@@@@@@@@@ COMMAND STATES @@@@@@@@@@@@@@@@@@@@@@@@


    def check_battery(self):
        self.debug("Checking battery charge")
        self.send_command("AT+CBC", {"+CBC:": self.read_battery_charge})


    def check_temperature(self ):
        self.debug("Checking temperature")
        self.send_command("AT+CMTE?", {"+CMTE:": self.read_temperature}, 2) # Takes some time to get a response


    def check_signal_strenght(self):
        self.debug("Checking signal strenght")
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
            self.debug("Battery charge : "+str(batteryState.iPercent)+"%"+" "+str(batteryState.iVoltage)+"mV")
        except Exception:
            self.dCommandStates[BATTERY_STATE].iState = -1
            self.exception("An error occured while reading battery charge : \n" )


    #Response type : +CMTE: 0,23.73
    def read_temperature(self, sResponse):
        try:
            values = sResponse.split()[1] # "0, 23.73 "
            values = values.split(',') # [ 0, 23.73 ]
            tempState = self.dCommandStates[TEMPERATURE_STATE]
            tempState.fDegres = float(values[1]) # 23.73
            self.debug("Temperature : " + str(tempState.fDegres))
        except Exception:
            self.dCommandStates[TEMPERATURE_STATE].iState = -1
            self.exception("An error occured while reading temperature : \n" )

    # Response type : +CSQ: 15,0
    def read_signal_strength(self, sResponse):
        try:
            values = sResponse.split()[1]
            values = values.split(',')
            signalState = self.dCommandStates[SIGNAL_STATE]
            signalState.iStrenght = int(values[0])
            self.debug("Signal Strenght : "+str(signalState.iStrenght))
        except Exception:
            self.dCommandStates[SIGNAL_STATE].iState = -1
            self.exception("An error occured while reading signal strenght : \n")

    # Response type = OK or ERROR
    def read_cmgf(self, sResponse):

        CMGFState = self.dCommandStates[CMGF_STATE]
        CMGFState.iSmsMode = 0
        try:
            value = sResponse.split()[0]
            if value == "OK":
                CMGFState.iSmsMode = 1
                self.debug("CMFG STATE is 1")
        except Exception:
            self.exception("An error occured while reading battery CMFG state : \n")


    # Response type = OK or ERROR
    def read_netlight(self, sResponse):
        try:
            value = sResponse.split()[0]
            if value == "OK":
                self.info("Netlight is OFF")
        except Exception:
            self.exception("An error occured while reading netlight response : \n" )


class SmsToSend():

    SMS_SEND_SUCCESS = 1
    SMS_SEND_IN_QUEUE = 0
    SMS_SEND_FAILED = -1

    def __init__(self, sMessage, lNumbers, tMaxTryTime = DEFAULT_MAX_TRY_TIME, iPriority = 0 ):
        self.sMessage = sMessage # The message
        self.lNumbers = lNumbers # List of telephone numbers
        self.iPriority = iPriority # Not sure if it will be used
        self.dtCreationDate = datetime.now()
        self.dtLastSendTry = datetime.min
        self.iSendState = SmsToSend.SMS_SEND_IN_QUEUE
        self.tMaxTryTime =  tMaxTryTime

    def log_str(self):

        sLog = "-- SMS S --\n"
        sLog += "Numbers : "+str(self.sNumbers) + "\n"
        sLog += "Created : "+str(self.dtCreationDate) + "\n"
        sLog += "Last try : "+str(self.dtLastSendTry) + "\n"
        sLog += "State : " + str(self.iSendState) + "\n"
        sLog += "Content : \n" + self.sMessage
        return sLog


class SmsReceived():

    def __init__(self, sMessage, iMemIndex, sSender, sDate):
        self.sMessage = sMessage
        self.iMemIndex = iMemIndex
        self.sSender = sSender
        self.sDateReceivedSMS = sDate # String format
        self.dtDateReceivedModule = datetime.now()

    def log_str(self):

        sLog = "-- SMS R --\n"
        sLog += "Sender : " + self.sSender + "\n"
        sLog += "Received at : "+str(self.sDateReceivedSMS) + " -- "+str(self.dtDateReceivedModule) + "\n"
        sLog += "Memory index = "+str(self.iMemIndex) + "\n"
        sLog += "Content : \n" + self.sMessage
        return sLog