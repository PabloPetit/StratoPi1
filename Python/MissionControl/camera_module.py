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

        self.bIsRecording = False
        self.dtStartRecoding = datetime.min
        self.dtLastCapture = datetime.min

        self.iCaptureCount = 0
        self.iVideoCount = 0

        self.oCurrentSetting = None

        self.oCam = None
        self.bCaptureOk = False

    def setup(self):
        super(CameraModule, self).setup()
        try:
            self.oCam = PiCamera()
        except:
            self.exception("Failed to create Camera object")
            self.oCam = None
        if self.oCam != None:
            try:
                time.sleep(2)
                self.oCam.capture(CAMERA_CAPTURE_PATH+"warm_up.png")
                self.bCaptureOk = True
            except:
                self.exception("Failed to warm up camera")

    def create_periodical_checks(self):
        self.add_periodical_checks(MEMORY_STATE, MemoryState(self.read_free_memory, MEMORY_REFRESH_TIMEOUT, MEMORY_STATE))

    def send_raw_log(self):
        pass

    def evaluate_module_ready(self):
        return self.oCam is not None and self.bCaptureOk


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

        self.select_camera_setting()

        self.apply_camera_setting()

        self.manage_capture()

        self.manage_record()





    def select_camera_setting(self):
        return CAMERA_MAX_SETTING # For now, next do stuff with altitude,

    def apply_camera_setting(self):
        self.oCam.resolution = self.oCurrentSetting.lVideoResolution
        self.oCam.framerate = self.oCurrentSetting.iFPS


    def manage_capture(self):
        pass

    def manage_record(self):

        if self.bIsRecording :
            if self.oCurrentSetting.bRecordVideo:

            else:
                self.oCam.stop_recording()
                self.bIsRecording = False
        else:
            if self.oCurrentSetting.bRecordVideo:


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@ PERIODICAL CHECKS @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

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


#@@@@@@@@@@@@@@@@@@@@@@@@@@@ MODULE FUNCTIONS @@@@@@@@@@@@@@@@@@@@@

    def check_self_integrity(self):
        return True

    def handle_no_integrity(self):
        pass

    def send_raw_log(self): #
        pass




# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@ CAMERA SETTINGS @@@@@@@@@@@@@@@@@@@@



class CameraSetting():
    def __init__(self,
                 lCaptureResolution=(3280, 2464),
                 lVideoResolution=(1920, 1080),
                 iFPS=30,
                 iCaptureQuality = 100,
                 iVideoQuality=10,
                 bRecordVideo=True,
                 bRecordCapture=True,
                 tCaptureInterval=timedelta(seconds=30),
                 tVideoDuration=timedelta(minutes=15)
                 ):
        self.lCaptureResolution = lCaptureResolution
        self.lVideoResolution = lVideoResolution
        self.iFPS = iFPS
        self.iCaptureQuality = iCaptureQuality
        self.iVideoQuality = iVideoQuality  # Range [40, 10] 10 where Very High for h.264, [0, 100] for mjpeg
        self.bRecordVideo = bRecordVideo
        self.bRecordCapture = bRecordCapture

        self.tCaptureInterval = tCaptureInterval
        self.tVideoDuration = tVideoDuration

# @@@@@@@@@@@@@@@@@@@ MAIN STARTUP @@@@@@@@@@@@@@@@@@@@@@@@@@@

WAIT_FOR_STARTUP_SLEEP = 5
WAIT_FOR_CONFIRMATION_SMS_SLEEP = 5
WAIT_FOR_MISSION_LAUNCH_SLEEP = 0.05

CONFIRMATION_BLINK_INTERVAL = 0.5
CONFIRMATION_BLINK_TIME = timedelta(seconds=10)
















