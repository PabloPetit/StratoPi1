from module import *


"""
    NOTE : An OSError is raised when the module is unplugged 
    Is it usefull to handle it ?

"""

class UartModule(Module):

    def __init__(self, oMainLog, sPort = DEFAULT_UART_PORT):
        Module.__init__(self, oMainLog)

        self.name = "DefaultUARTModuleName"

        self.sPort = sPort
        self.iBauds = DEFAULT_BAUDS
        self.oSer = None
        self.dDebuffer_dict = {}

        self.bIsOpen = False


    def setup(self):
        super(UartModule, self).setup()
        self.create_debuffer_dict()
        self.open_serial()


    def create_debuffer_dict(self):
        raise NotImplementedError("create_debuffer_dict not implemented")

    def create_periodical_checks(self):
        raise NotImplementedError("create_command_states not implemented")

#@@@@@@@@@@@@@@@@@@@@@@@@@@@ UART @@@@@@@@@@@@@@@@@@@@@@@@

    def open_serial(self):

        try:
            self.oSer= serial.Serial(self.sPort, self.iBauds)# No timeout set as it can raise an exception
            self.bIsOpen = True
            self.info("Serial Opened")
        except ValueError:
            self.exception("Value error when creating serial connection with uart module : ")
        except serial.SerialException:
            self.exception("Value error when creating serial connection with uart module : ")


#@@@@@@@@@@@@@@@@@@@@@@@@@@@ MODULE @@@@@@@@@@@@@@@@@@@@@@@@

    def check_self_integrity(self):
        raise NotImplementedError("check_self_integrity not implemented")

    def handle_no_integrity(self):
        raise NotImplementedError("handle_no_integrity not implemented")

    def module_run(self):
        raise NotImplementedError("module_run not implemented")

    def end_run(self):
        if self.oSer is not None:
            try:
                self.oSer.close()
            except:
                self.exception("Could not close serial")
# @@@@@@@@@@@@@@@@@@@@@@@ COMMANDS MANAGEMENT @@@@@@@@@@@@@@@@@@@@@@@@@

    def write_command(self, command):
        try:
            sCommand = remove_special_characters( command)
            sCommand+="\r\n"
            self.oSer.write(sCommand.encode("ascii"))
        except OSError:
            self.exception(" --- UART NOT FOUND ---")

    def read_buffer(self, bGetRaw = False):
        try:
            buffer = self.oSer.read_all()

            if len(buffer) > 0 and buffer[0] >= 128:
                self.error("None ascii data received, buffer flushed and re-read")
                self.oSer.flush()
                buffer = self.oSer.read_all()

            if bGetRaw:
                return buffer
            buffer = buffer.decode("ascii")
            buffer = buffer.replace("\r\n\r\n", '|')
            buffer = buffer.replace("\r\r\n", '|')  # TODO :NO NO NO NO NO ! Find something better !
            buffer = buffer.split('|')
            return buffer

        except serial.SerialTimeoutException:
            self.exception("Serial read Error : ")
            return "" if not bGetRaw else b""
        except AttributeError: #Can be the case where open_serial hasn't been called
            self.exception("Serial read Error : ")
            return "" if not bGetRaw else b""
        except Exception:
            self.exception("Serial read Error : ")
            return "" if not bGetRaw else b""


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
        self.debug("Checking AT")
        self.dPeriodicalChecks[AT_STATE].iState = 1
        self.send_command( "AT", { "OK" : self.set_at_ok_true } )
        return True


# @@@@@@@@@@@@@@@@@@@@@@@@ RESPONSE FUNCTIONS @@@@@@@@@@@@@@@@@@@@@

    """
        Response function have to take the response string as an argument, to avoid TypeError exception
    """

    def set_at_ok_true(self, sResponse):
        self.dPeriodicalChecks[AT_STATE].iState = 1
        self.debug("AT OK")



#  @@@@@@@@@@@@@@@@@@@@@@@@ USEFULL FUNCTIONS @@@@@@@@@@@@@@@@@@@@@

def remove_special_characters(command):
    return str(command).replace("\r", "").replace("\n", "")

def is_valid_baud( i_bauds ):

    if i_bauds not in [ 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200 ]: # SIM800 Authorized baud-rates
        return False

    return True