from uart_module import *
from queue import *
import RPi.GPIO as GPIO

class GsmModule( UartModule ):

    def __init__(self, oMainLog, sPort):
        UartModule.__init__(self, oMainLog, sPort)

        self.name = GSM_NAME
        self.sLogPath = GSM_LOG_PATH
        self.fUpdateDelay = GSM_UPDATE_DELAY

        self.qSms_to_send = Queue()
        self.lSmsReceived = []

        self.dSms_commands = {
            "STATE" : self.send_state,
            "CONFIRM" : self.confirm_network,
            "REG" : self.register_numbers,
            "LOCATION" : self.send_location,
            "END_MISSION" : self.end_mission,
            "SHUTDOWN" : self.shutdown
        }

        self.default_sms_command = self.send_default_sms

        self.oCurrentSmsMessage = None

        # Reset
        self.dtATCheckNotPassed = None
        self.dtZeroByteReceived = None
        self.dtLastHardReset = None


    def setup(self):
        super(GsmModule, self).setup()
        self.at_check()
        self.set_CMGF_state()
        #self.close_net_light()

    def create_periodical_checks(self):
        self.add_periodical_checks(AT_STATE, ATState(self.at_check, AT_REFRESH_TIMEOUT, AT_STATE))
        self.add_periodical_checks(BATTERY_STATE, BatteryState(self.check_battery, BATTERY_REFRESH_TIMEOUT, BATTERY_STATE))
        self.add_periodical_checks(TEMPERATURE_STATE, TemperatureState(self.check_temperature, TEMPERATURE_REFRESH_TIMEOUT, TEMPERATURE_STATE))
        self.add_periodical_checks(SIGNAL_STATE, SignalState(self.check_signal_strenght, SIGNAL_REFRESH_TIMEOUT, SIGNAL_STATE))
        self.add_periodical_checks(CMGF_STATE, CMGFState(self.set_CMGF_state, CMGF_REFRESH_TIMEOUT, CMGF_STATE))

    def create_debuffer_dict(self):
        self.dDebuffer_dict[str(B_NULL)] = self.zero_byte
        #Message received log ?

    def send_raw_log(self): # BatPercent, BatVoltage, temp, signal
        oBat = self.dPeriodicalChecks[BATTERY_STATE]
        oTemp = self.dPeriodicalChecks[TEMPERATURE_STATE]
        oSign = self.dPeriodicalChecks[SIGNAL_STATE]
        try:
            sRawLog = str(oBat.iPercent)+","+str(oBat.iVoltage)+","+str(oTemp.fDegres)+","+str(oSign.iStrenght)
            self.oRawLog().info(sRawLog)
        except:
            self.warning("Error when sending raw log")

# @@@@@@@@@@@@@@@@@@@@@@@@ MODULE FUNCTIONS @@@@@@@@@@@@@@@@@@@


    def evaluate_module_ready(self):
        oSignalState = self.dPeriodicalChecks[SIGNAL_STATE]
        oCMFGState = self.dPeriodicalChecks[CMGF_STATE]
        self.bIsReady = oCMFGState.iState > 0 and oSignalState.iStrenght > READY_MINIMAL_SIGNAL


    def check_self_integrity(self):

        bAtState = self.dPeriodicalChecks[AT_STATE].iState > 0
        bZeroByte = self.dtZeroByteReceived is None

        if bAtState:
            self.dtATCheckNotPassed = None
            self.dtZeroByteReceived = None
        elif self.dtATCheckNotPassed is None:
            self.critical("Setting AT check not passed")
            self.dtATCheckNotPassed = datetime.now()

        return bAtState and bZeroByte

    def handle_no_integrity(self):

        dtRefDate = None

        if self.dtZeroByteReceived and self.dtATCheckNotPassed:
            dtRefDate = min(self.dtZeroByteReceived, self.dtATCheckNotPassed)
        elif self.dtZeroByteReceived:
            dtRefDate = self.dtZeroByteReceived
        elif self.dtATCheckNotPassed:
            dtRefDate = self.dtATCheckNotPassed
        else:
            self.critical("CODE ERROR - Should not happen. Reference date not found for handle_no_integrity")

        if dtRefDate:

            tHardResetCountdown = GSM_HARD_RESET_DELAY - ( datetime.now() - dtRefDate )
            self.critical("Handling no integrity\n" +
                          "        AT check not passed at : " + str(self.dtATCheckNotPassed) +
                          "        Zero byte received at : " +str(self.dtZeroByteReceived) +
                          "        Remaining Time Before Hard Reset : "+str(tHardResetCountdown))

            if tHardResetCountdown.days < 0:
                self.hard_reset()



    def zero_byte(self, sResponse):
        self.critical("Zero byte received")
        if self.dtZeroByteReceived is None:
            self.critical("Setting zero byte receive date")
            self.dtZeroByteReceived = datetime.now()

    def module_run(self):
        self.manage_sms_queue()
        self.manage_sms_reception()

    def end_run(self):
        #TODO: Send AT+CPOWD=1
        self.send_command("AT+CPOWD=1", {})
        super(GsmModule, self).end_run()

# @@@@@@@@@@@@@@@@@@@@@@@@ HARD RESET @@@@@@@@@@@@@@@@@@@@@


    def hard_reset(self):
        self.critical("HARD RESET")
        self.dtATCheckNotPassed = None
        self.dtZeroByteReceived = None
        self.dtLastHardReset = datetime.now()
        self.critical("Pulling Reset cicuit to ground for : "+str(GSM_RESET_HIGH_LEVEL_TIME)+" seconds ...")
        GPIO.output(GSM_RESET_PIN, GPIO.HIGH)
        time.sleep(GSM_RESET_HIGH_LEVEL_TIME)
        GPIO.output(GSM_RESET_PIN, GPIO.LOW)
        self.critical("Hard reset done")



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
            self.warning("Prefix not found, sending default sms")
            self.default_sms_command(oSms)
        except Exception:
            self.exception("An error occured while switching on SMS prefix : \n")


    def check_memory_overload(self):
        pass


# @@@@@@@@@@@@@@@@@@@@@@@@ SMS SENDING @@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    def manage_sms_queue(self):
        self.debug("Managing sms queue")
        if  self.qSms_to_send.empty():
            return

        try:
            oSms = self.qSms_to_send.get()

            for n in oSms.lNumbers:
                self.send_sms(oSms, n)
        except:
            self.exception("Exception while managing sms to send queue")


    def send_sms(self, oSms, sNumber):
        try:
            self.oCurrentSmsMessage = oSms
            self.oCurrentSmsMessage.dtLastSendTry = datetime.now()
            sCom = "AT+CMGS=\""+sNumber+"\""
            self.send_command(sCom, {'>' : self.write_sms, "ERROR" : self.sms_send_error})
        except:
            self.exception("Exception while trying to send sms")

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
            oBatteryState = self.dPeriodicalChecks[BATTERY_STATE]
            oSignalState = self.dPeriodicalChecks[SIGNAL_STATE]
            oTempState = self.dPeriodicalChecks[TEMPERATURE_STATE]
            sMessage = "BATTERY : "+str(oBatteryState.iPercent)+"% "+str(oBatteryState.iVoltage)+"mV\n"
            sMessage += "SIGNAL : "+str(oSignalState.iStrenght)+"\n"
            sMessage +="TEMP : "+str(oTempState.fDegres)+"\n"
            lNumberList = [ oSms.sSender.replace('"', "")]
            oSmsToSend = SmsToSend(sMessage, lNumberList)
            self.qSms_to_send.put(oSmsToSend)
            self.info("Sending STATE response to : "+str(lNumberList)+" Content : \n"+oSmsToSend.log_str(), True)
        except Exception:
            self.exception("An error occured while trying to send current state : \n")

    def register_numbers(self, oSms):
        try:
            self.info("Registrering numbers", True)
            global dTelephone_numbers
            lNumbers = oSms.sMessage.split()
            lNumbers = lNumbers[1:]
            for num in lNumbers:
                if self.is_valid_number(num):
                    sIndex = "NUM"+str(len(dTelephone_numbers.keys()))
                    dTelephone_numbers[sIndex] = num
                    self.info(num+" registerd")
                else:
                    self.warning("Invalid number : "+num)
        except:
            self.exception("Exception while reading REG sms")

    def is_valid_number(self, number):
        return True

    def confirm_network(self, oSms):
        self.info("Network Confirmation SMS received", True)
        global bConfirmSMSReceived
        bConfirmSMSReceived = True

    def send_location(self, oSms):
        try:
            self.info("Sending location")
        except:
            self.exception("Exception while reading LOCATION sms")

    def send_default_sms(self, oSms):
        try:
            self.info("Sending default sms", True)
            self.send_state(oSms)
            self.send_location(oSms)
        except:
            self.exception("Exception while reading LOCATION sms")

    def end_mission(self, oSms):
        try:
            self.info("End mission sms received")
        except:
            self.exception("Exception while ending mission")

    def shutdown(self, oSms):
        try:
            self.info("Shutdown sms received")
            self.critical("SHUTING DOWN RASPBERRY")
            os.system("sudo shutdown now")
        except:
            self.exception("Exception while shuting down raspi")



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
    """

    #Response type : +CBC: 0,85,4087
    def read_battery_charge(self, sResponse):
        try:
            values = sResponse.split()[1]
            values = values.split(',') # [0, 85, 4087]
            batteryState = self.dPeriodicalChecks[BATTERY_STATE]
            batteryState.iPercent = int(values[1]) # 85
            batteryState.iVoltage = int(values[2]) # 4087
            self.debug("Battery charge : "+str(batteryState.iPercent)+"%"+" "+str(batteryState.iVoltage)+"mV")
        except Exception:
            self.dPeriodicalChecks[BATTERY_STATE].iState = -1
            self.exception("An error occured while reading battery charge : \n" )


    #Response type : +CMTE: 0,23.73
    def read_temperature(self, sResponse):
        try:
            values = sResponse.split()[1] # "0, 23.73 "
            values = values.split(',') # [ 0, 23.73 ]
            tempState = self.dPeriodicalChecks[TEMPERATURE_STATE]
            tempState.fDegres = float(values[1]) # 23.73
            self.debug("Temperature : " + str(tempState.fDegres))
        except Exception:
            self.dPeriodicalChecks[TEMPERATURE_STATE].iState = -1
            self.exception("An error occured while reading temperature : \n")

    # Response type : +CSQ: 15,0
    def read_signal_strength(self, sResponse):
        try:
            values = sResponse.split()[1]
            values = values.split(',')
            signalState = self.dPeriodicalChecks[SIGNAL_STATE]
            signalState.iStrenght = int(values[0])
            self.debug("Signal Strenght : "+str(signalState.iStrenght))
        except Exception:
            self.dPeriodicalChecks[SIGNAL_STATE].iState = -1
            self.exception("An error occured while reading signal strenght : \n")

    # Response type = OK or ERROR
    def read_cmgf(self, sResponse):

        CMGFState = self.dPeriodicalChecks[CMGF_STATE]
        CMGFState.iSmsMode = 0
        try:
            value = sResponse.split()[0]
            if value == "OK":
                CMGFState.iSmsMode = 1
                self.debug("CMFG STATE is 1")
            else:
                self.warning("No OK response received on CMFG request : "+value)
        except Exception:
            self.exception("An error occured while reading battery CMFG state : \n")


    # Response type = OK or ERROR
    def read_netlight(self, sResponse):
        try:
            value = sResponse.split()[0]
            if value == "OK":
                self.info("Netlight is OFF")
            else:
                self.warning("No OK response received on NETLIGHT OFF request : " + value)
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
        sLog += "Numbers : "+str(self.lNumbers) + "\n"
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