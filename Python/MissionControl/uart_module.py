from module import *
from config import *
import serial
import time

"""
    NOTE : An OSError is raised when the module is unplugged 
    Is it usefull to treat it ?

"""

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
            self.oSer= serial.Serial(self.s_port, self.i_bauds)# No timeout set as it can raise an exception
        except ValueError:
            print("Value error when creating serial connection with uart module")
        except serial.SerialException:
            print("Value error when creating serial connection with uart module")
        self.at_check()


#@@@@@@@@@@@@@@@@@@@@@@@@@@@ MODULE @@@@@@@@@@@@@@@@@@@@@@@@

    def check_self_integrity(self):
        self.at_check()
        return self.bAt_ok

    def handle_no_integrity(self):
        pass

    def module_run(self):
        pass

    def log(self):
        pass


# @@@@@@@@@@@@@@@@@@@@@@@ COMMANDS MANAGEMENT @@@@@@@@@@@@@@@@@@@@@@@@@

    def write_command(self, command):
        sCommand = remove_special_characters( command)
        self.oSer.write(sCommand.encode("ascii"))
        self.oSer.flush()

    def read_buffer(self):
        buffer = ""
        try:
            buffer = self.oSer.read_all()
        except serial.SerialTimeoutException:
            pass
        buffer = buffer.decode("ascii")
        return buffer.split("\r\n\r\n").split("\r\r\n") # Black Magic, trust me

    def clear_buffer(self):

        buffer = self.read_buffer()
        self.manage_response( buffer, self.dDebuffer_dict )

    def manage_response( self, buffer, action_dict ):
        non_used_buffer = []

        for s in buffer :
            #TODO : wrong, must only consider prefixe and send full line to action_cict function
            if s in action_dict.keys() : # What if response has no prefixe ?
                action_dict[s](s)
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
        self.oLock.aquire()
        self.bAt_ok = False
        self.send_command( "AT", { "OK" : self.set_at_ok_true } )
        self.oLock.release()
        return True


# @@@@@@@@@@@@@@@@@@@@@@@@ RESPONSE FUNCTIONS @@@@@@@@@@@@@@@@@@@@@

    def set_at_ok_true( self ):
        self.bAt_ok = True

#  @@@@@@@@@@@@@@@@@@@@@@@@ USEFULL FUNCTIONS @@@@@@@@@@@@@@@@@@@@@

def remove_special_characters(self, command):
    return str(command).replace("\r", "").replace("\n", "")

def is_valid_baud( self, i_bauds ):

    if i_bauds not in [ 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200 ]: # SIM800 Authorized baud-rates
        return False

    return True