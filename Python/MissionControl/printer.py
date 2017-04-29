from module import  *
import os


PRIORITY_HIGH = 1 # will be written in the main channel
PRIORITY_LOW = 0

class Printer( Module ):

    """
        Maximum number of logs red in one loop. Used to allow save and module runtime functions
        in the case where logs are processed slower than they arrive
    """
    MAX_LOOP_LOGS = 2048

    def __init__(self, sHome_path):
        Module.__init__()
        self.sHome_Path = sHome_path
        self.dChannels = {}

        self.qLog = Queue()
        self.create_home_path()
        self.open_channels()

    def create_home_path(self):
        try:
            if not os.path.isdir(self.sHome_Path):
                os.makedirs(self.sHome_Path)
        except FileExistsError:
            print("Home path already exists")




    def open_channels(self):

        bAll_channels_ok = True

        for channel in CHANNELS_PATHS:
            sPath = self.sHome_Path + "/"+channel.value
            oChan = Channel(sPath, channel)
            self.dChannels[channel] = oChan
            if not oChan.open_channel():
                bAll_channels_ok = False

        if not bAll_channels_ok:
            print("Could not open all channels")


    def log(self, oLog):
        pass


# @@@@@@@@@@@@@@@@@@@ MODULE OVERRIDE @@@@@@@@@@@@@@@@@@@@@@@@@@

    def create_command_states(self):
        pass

    def check_self_integrity(self):
        pass

    def handle_no_integrity(self):
        pass

    def module_run(self):
        self.read_queue()

    def send_log(self):
        pass

#@@@@@@@@@@@@@@@@@@@@@@@ PRINTER RUN @@@@@@@@@@@@@@@@@@@@@@@@@@

    def read_queue(self):
        i = 0
        try:
            while not self.qLog.empty() and i < Printer.MAX_LOOP_LOGS:
                oLog = self.qLog.get()
                self.dChannels[oLog.eChannel].send_log(oLog)
                i += 1

        except Exception:
            pass

# @@@@@@@@@@@@@@@@@@@@@@ CLASS LOG @@@@@@@@@@@@@@@@@@@@@@@@@@@@@


class Log():

    def __init__(self, eChannel, sData, iPriotity = PRIORITY_HIGH ):
        self.eChannel = eChannel
        self.sData = sData
        self.iPriority = iPriotity
        self.dtEmitDate = datetime.now()

    def get_log(self):
        return "[ "+self.eChannel.name+" ] "+str(self.dtEmitDate)+" - "+self.sData

# @@@@@@@@@@@@@@@@@@@@@@ CLASS CHANNEL @@@@@@@@@@@@@@@@@@@@@@@@@

class Channel():

    def __init__(self, sPath, eChanPath):

        self.sPath = sPath
        self.eChanPath = eChanPath
        self.oFile = None
        self.dtLastSave = datetime.min
        self.lBuffer = []

    def open_channel(self):
        try:
            oFile = open(self.sPath,"a+")
            return True
        except Exception:
            return False

    def log(self, oLog):
        pass

    def save_on_disk(self):
        pass

    def close_channel(self):
        pass



class CHANNELS_PATHS(Enum):

    MAIN = "Main" # The human readable log with all the important information
    GSM = "Gsm"
    CAMERA = "Cam"
    PRINTER = "Printer"

