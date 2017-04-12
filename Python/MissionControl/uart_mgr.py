from module import  *
from threading import *

import serial
import time


s_defautl_port = '/dev/cu.usbserial-A503S1B9'
i_default_timeout = 2000

i_sleep_step = 50

# Sim800l configuration match serial.Serial() default configuration
i_default_bauds = 115200
i_default_byte_size = serial.EIGHTBITS
i_default_parity = serial.PARITY_NONE
i_defual_stop_bits = serial.STOPBITS_ONE



class UartMgr( Module ):

    def __init__( self, s_port = s_defautl_port, i_bauds = i_default_bauds ):
        Module.__init__()
        self.s_port = s_port
        self.i_bauds = i_bauds
        self.o_ser = None
        self.debuffer_dict = {}

        #state

        self.b_at_ok = False

#@@@@@@@@@@@@@@@@@@@@@@@ CONNEXION @@@@@@@@@@@@@@@@@@@@@@@@@

    def open_serial( self ):
        if not is_valid_baud( self.i_bauds ):
            return False

        self.o_ser = serial.Serial( self.s_port, self.i_bauds, timeout=i_default_timeout )


        self.at_check()


    def reconnect(self, i_timeout = 10000):
        pass

    def close_connexion( self ):
        pass

# @@@@@@@@@@@@@@@@@@@@@@@ COMMANDS MANAGEMENT @@@@@@@@@@@@@@@@@@@@@@@@@

    def write_command(self, command):
        sCommand = remove_special_characters( command)
        self.o_ser.write(sCommand.encode("ascii"))
        self.o_ser.flush()

    def read_buffer(self):

        buffer = self.o_ser.read_all()
        buffer = buffer.decode("ascii")
        return buffer.splitlines()

    def clear_buffer(self):

        buffer = self.read_buffer()
        self.manage_response( buffer, self.debuffer_dict )

    def manage_response( self, buffer, action_dict ):
        #action_dict = action_dict ^ self.debuffer_dict
        non_used_buffer = []

        for s in buffer :
            if s in action_dict.keys() : # What if response has no prefixe ?
                action_dict[s]()
            else :
                non_used_buffer.append( s )

        return non_used_buffer

    def send_command( self, command, resp_actions_dict = {}, wait_delay = i_default_timeout,  ):

        self.clear_buffer()
        self.write_command( command )

        buffer = ""

        while wait_delay > 0 or ( buffer == "" and ):
            time.sleep( min ( i_sleep_step, wait_delay ) )
            wait_delay -= i_sleep_step
            #Check each step if commands done
            #How to manage multiple line response ?

        buffer = self.read_buffer()

        buffer = self.manage_response( buffer, resp_actions_dict )
        self.manage_response( buffer, self.debuffer_dict )


 # @@@@@@@@@@@@@@@@@@@@@@@ COMMANDS @@@@@@@@@@@@@@@@@@@@@@@@@


    def at_check(self):

        self.b_at_ok = False

        resp_action_dict = { "OK" : self.set_at_ok_true }

        self.send_command( "AT", resp_action_dict )

        return True


# @@@@@@@@@@@@@@@@@@@@@@@@ RESPONSE FUNCTIONS @@@@@@@@@@@@@@@@@@@@@

    def set_at_ok_true( self ):
        self.b_at_ok = True

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@  RUN  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def run(self):
        pass


"""
    USEFULL FUNCTIONS
"""

def remove_special_characters(self, command):
    return str(command).replace("\r", "").replace("\n", "")

def format_command(self, command):

    formatted_command = remove_special_characters(command)
    formatted_command = formatted_command.encode( "ascii" )  # conversion in bytes

    return formatted_command


def is_valid_baud( self, i_bauds ):

    if i_bauds not in [ 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200 ]: # SIM800 Authorized baud-rates
        return False

    return True