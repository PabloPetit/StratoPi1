from module import *
from config import *
import serial


class UartModule( Module ):

    def __init__( self, oLock, fDelay ):
        Module.__init__( self, oLock, fDelay )

        self.sPort = sDefautl_port
        self.iBauds = iDefault_bauds
        self.oSer = None
        self.dDebuffer_dict = {}

        #state

        self.bAt_ok = False


#@@@@@@@@@@@@@@@@@@@@@@@@@@@ UART @@@@@@@@@@@@@@@@@@@@@@@@

    def open_serial(self):

        self.o_ser = serial.Serial(self.s_port, self.i_bauds, timeout=i_default_timeout)

        self.at_check()


#@@@@@@@@@@@@@@@@@@@@@@@@@@@ MODULE @@@@@@@@@@@@@@@@@@@@@@@@

    def check_self_integrity(self):
        return self.bAt_ok

    def handle_no_integrity(self):
        pass

    def module_run(self):
        raise NotImplementedError("module_run not implemented")

    def log(self):
        pass