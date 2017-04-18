from module import *
import serial

"""
    NOTE : An OSError is raised when the module is unplugged 
    Is it usefull to treat it ?

"""

AT_STATE = "at"

class UartModule( Module ):

    def __init__(self, fUpdateDelay):
        Module.__init__(self,  fUpdateDelay)

        self.sPort = DEFAULT_UART_PORT
        self.iBauds = DEFAULT_BAUDS
        self.oSer = None
        self.dDebuffer_dict = {}
        self.name = "Default UART Module Name"

    def create_command_states(self):
        raise NotImplementedError("create_command_states not implemented")

#@@@@@@@@@@@@@@@@@@@@@@@@@@@ UART @@@@@@@@@@@@@@@@@@@@@@@@

    def open_serial(self):

        bIsOpen = False
        try:
            self.oSer= serial.Serial(self.sPort, self.iBauds)# No timeout set as it can raise an exception
        except ValueError:
            print("Value error when creating serial connection with uart module")
        except serial.SerialException:
            print("Value error when creating serial connection with uart module")

        self.at_check()


#@@@@@@@@@@@@@@@@@@@@@@@@@@@ MODULE @@@@@@@@@@@@@@@@@@@@@@@@

    def check_self_integrity(self):
        raise NotImplementedError("check_self_integrity not implemented")

    def handle_no_integrity(self):
        raise NotImplementedError("handle_no_integrity not implemented")

    def module_run(self):
        raise NotImplementedError("module_run not implemented")

    def log(self):
        raise NotImplementedError("log not implemented")


# @@@@@@@@@@@@@@@@@@@@@@@ COMMANDS MANAGEMENT @@@@@@@@@@@@@@@@@@@@@@@@@

    def write_command(self, command):
        sCommand = remove_special_characters( command)
        sCommand+="\r\n"
        self.oSer.write(sCommand.encode("ascii"))
        # Note : Flush clear the buffer, remember not to do it

    def read_buffer(self):
        buffer = ""
        try:
            buffer = self.oSer.read_all()
            buffer = buffer.decode("ascii")
            buffer = buffer.replace("\r\n\r\n", '|')
            buffer = buffer.replace("\r\r\n", '|')  # TODO :NO NO NO NO NO ! Find something better !
            return buffer.split('|')  # Black Magic, trust me

        except serial.SerialTimeoutException:
            return ""
        except AttributeError: #Can be the case where open_serial hasn't been called
            return ""
        except Exception:
            return ""


    def clear_buffer(self):

        buffer = self.read_buffer()
        self.manage_response( buffer, self.dDebuffer_dict )

    def manage_response( self, buffer, action_dict ):

        non_used_buffer = []

        for s in buffer :
            sPrefixe = s.split()
            if len(sPrefixe) > 0:
                sPrefixe = sPrefixe[0]
                if sPrefixe in action_dict.keys() : # What if response has no prefixe ?
                    action_dict[sPrefixe](s)
                else :
                    non_used_buffer.append(s)

        return non_used_buffer

    def send_command(self, sCommand, dResp_actions = {}, fWait_delay = DEFAULT_UART_COMMAND_TIMEOUT):

        self.clear_buffer()
        self.write_command( sCommand )

        time.sleep( fWait_delay )

        buffer = self.read_buffer()

        buffer = self.manage_response( buffer, dResp_actions )# Might be better in two steps to avoid debuffer reading meaningfull responses
        self.manage_response( buffer, self.dDebuffer_dict )


 # @@@@@@@@@@@@@@@@@@@@@@@ COMMANDS @@@@@@@@@@@@@@@@@@@@@@@@@


    def at_check(self):
        self.oLock.acquire()
        self.dCommandStates[AT_STATE].iState = 1
        self.send_command( "AT", { "OK" : self.set_at_ok_true } )
        self.oLock.release()
        return True


# @@@@@@@@@@@@@@@@@@@@@@@@ RESPONSE FUNCTIONS @@@@@@@@@@@@@@@@@@@@@

    """
        Response function have to take the response string as an argument, to avoid TypeError exception
    """

    def set_at_ok_true(self, sResponse):
        self.dCommandStates[AT_STATE].iState = 1




# @@@@@@@@@@@@@@@@@@@@@@@@@@ COMMAND STATES @@@@@@@@@@@@@@@@@@@@@@@

class ATState(CommandState):

    def __init__(self, funCommand, fTimeout, sName):
        CommandState.__init__(self, funCommand, fTimeout, sName)



#  @@@@@@@@@@@@@@@@@@@@@@@@ USEFULL FUNCTIONS @@@@@@@@@@@@@@@@@@@@@

def remove_special_characters(command):
    return str(command).replace("\r", "").replace("\n", "")

def is_valid_baud( i_bauds ):

    if i_bauds not in [ 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200 ]: # SIM800 Authorized baud-rates
        return False

    return True