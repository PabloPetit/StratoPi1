from module import *
from picamera import *
import subprocess

class CameraModule(Module):
    def __init__(self, oMainLog):
        Module.__init__(self, oMainLog)

        self.name = CAMERA_NAME
        self.sLogPath = CAMERA_LOG_PATH
        self.fUpdateDelay = CAMERA_UPDATE_DELAY
        self.tMainLogInterval = DEFAULT_MAIN_LOG_INTERVAL

        self.bRecording = False

        self.iCaptureCount = 0
        self.iVideoCount = 0

        self.oCurrentSetting = None

    def setup(self):
        super(CameraModule, self).setup()
        #Try to capture an image

    def create_periodical_checks(self):
        self.add_periodical_checks(MEMORY_STATE, MemoryState(self.read_free_memory, MEMORY_REFRESH_TIMEOUT, MEMORY_STATE))

    def send_raw_log(self):
        pass

    def evaluate_module_ready(self):
        return True


    def module_run(self):

        #photos can be stored in png
        #remember to set video and photo quality
        #we can put thumbnail to none to gain some place

        # A Memory state could be a good idea is necessary

        # Keep the module run structure, change dynamically the self.updateDelay

        # 1 : Check and Set Camera setting
        # 2 : if needed, apply new Settings
        # 3 : Depending on camera settings :
        #       - Capture
        #       - Record Video
        # 4 : Set sleep time to minimum beetween Next Photo, Next Video

        pass



    def select_camera_setting(self):
        pass

    def apply_camera_setting(self):
        pass

    def read_free_memory(self):
        try:
            sMemState = subprocess.check_output(["df","-h"]).decode("ascii")
            lLines = sMemState.split("\n")
            lMainDisk = ""
            for l in lLines:
                if l.split()[0] == MAIN_DISK_PATH:
                    lMainDisk = l
                    break

            fSize = self.parse_size_string(lMainDisk[1])
            fUsed = self.parse_size_string(lMainDisk[2])
            fAvailable = self.parse_size_string(lMainDisk[3])
            fPercentUsed = int(lMainDisk[3].replace('%',''))

            if fSize != -1 and fUsed != -1 and fAvailable != -1 and fPercentUsed != -1:
                oMemState = self.dPeriodicalChecks[MEMORY_STATE]
                oMemState.fSize = fSize
                oMemState.fUsed = fUsed
                oMemState.fAvailable = fAvailable
                oMemState.fPercentUsed = fPercentUsed
            else:
                self.error("Memory State not red correctly, will not be updated")

        except:
            self.exception("Exeception while reading memory state")


    def parse_size_string(self, sSize):
        fSize = -1
        try:
            cSign = sSize[len(sSize)-1]
            iValue = float(sSize[0:(len(sSize)-1)])
            fSize = iValue
            if cSign == 'G':
                pass
            elif cSign == 'M':
                fSize /= 1024.0
            elif cSign == 'K':
                fSize /= (1024.0 * 1024.0)
            else:
                self.warning("Sign of data value not recognized :"+iValue)
                fSize = -1

        except:
            self.exception("Wrong memory size : "+str(sSize))

        return fSize

    def check_self_integrity(self):
        return True

    def handle_no_integrity(self):
        pass

    def send_raw_log(self): #
        pass























