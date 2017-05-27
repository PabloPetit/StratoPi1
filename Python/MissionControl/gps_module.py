from uart_module import *
import collections

class GPSModule(UartModule):

    def __init__(self, oMainLog, sPort):
        UartModule.__init__(self, oMainLog, sPort)

        self.name = GPS_NAME
        self.sLogPath = GPS_LOG_PATH
        self.fUpdateDelay = GPS_UPDATE_DELAY

        self.dqFixMemory = collections.deque(maxlen=GPS_MEMORY)

        self.fMaxAltitude = 0.0

        self.dTramePref = {
            GPRMC : self.read_GPRMC,
            GPVTG : self.read_GPVTG,
            GPGGA : self.read_GPGGA,
            GPGLL : self.read_GPGLL,
            GPGSA : self.read_GPGSA,
            GPGSV : self.read_GPGSV
        }

        self.oLastFix = None
        self.oCurrentFix = None
        self.sLastBuffer = ""


    def setup(self):
        super(GPSModule, self).setup()

    def create_periodical_checks(self):
        pass

    def create_debuffer_dict(self):
        pass

    def check_self_integrity(self):
        return True

    def handle_no_integrity(self):
        pass

    def send_raw_log(self):
        self.oRawLog.info(self.sLastBuffer)

    def send_log(self, bForwardMain):
        if self.oCurrentFix and self.oCurrentFix.bValid and self.oCurrentFix.iPositionFixIndicator > 0:
            self.info(self.oCurrentFix.log_str())

    def evaluate_module_ready(self):
        return self.oLastFix is not None # If first correct fix is acquired

    def module_run(self):
        try:
            self.sLastBuffer = self.read_buffer()
            self.oCurrentFix = GPSFix()
            self.read_gps_data()
            self.validate_fix()
        except:
            self.exception("Could not read buffer from GPS UART device")

    def validate_fix(self):

        if self.oCurrentFix and self.oCurrentFix.bValid and self.oCurrentFix.iPositionFixIndicator > 0:
            self.oLastFix = self.oCurrentFix
            self.dqFixMemory.appendleft(self.oCurrentFix)


    def read_gps_data(self):
        try:
            for sTempBuffer in self.sLastBuffer:
                for trame in sTempBuffer.split("\r\n"):
                    try:
                        sPrefixe = trame.split(",")[0].replace('$','')
                        self.dTramePref[sPrefixe](trame)
                    except Exception:
                        self.warning("Wrong Prefixe on GPS trame parsing : "+sPrefixe)
        except Exception:
            self.exception("Exception while reading GPS data")


    def read_GPGGA(self, sTrame):
        try:
            lValues = sTrame.split(',')

            self.set_gps_time(lValues[1])
            self.oCurrentFix.sLatitude = lValues[2]
            self.oCurrentFix.sNSIndicator = lValues[3]
            self.oCurrentFix.sLongitude = lValues[4]
            self.oCurrentFix.sEWIndicator = lValues[5]
            try:
                self.oCurrentFix.iPositionFixIndicator = int(lValues[6])
                self.oCurrentFix.iSatUsed = int(lValues[7])
                self.oCurrentFix.fHDOP = float(lValues[8])
                self.oCurrentFix.fAltitudeMSL = float(lValues[9])
                self.oCurrentFix.fGeoid = float(lValues[11])
            except:
                self.warning("Could not read GGA number info ( Fix indicator, nbSatUsed, HDOP, MSL, Geoid )")

        except:
            self.oCurrentFix.bValid = False
            self.warning("Exception while parsing GPGGA trame : " + sTrame, False)

    def read_GPRMC(self, sTrame):
        try:
            lValues = sTrame.split(',')
            self.set_gps_date(lValues[9])
            try:
                self.oCurrentFix.fSpeedOverGround = knots_to_kph(float(lValues[7])) # kph
                self.oCurrentFix.fCourseOverGround = float(lValues[8]) # degres
            except:
                self.debug("No data for speed over ground or course over ground")

        except Exception:
            self.warning("Exception while parsing GPRMC trame : "+sTrame, False)

    def read_GPVTG(self, sTrame):
        pass

    def read_GPGLL(self, sTrame):
        pass

    def read_GPGSA(self, sTrame):
        pass

    def read_GPGSV(self, sTrame):
        try:
            lValues = sTrame.split(',')
            self.oCurrentFix.iSatInView = int(lValues[3])
        except:
            self.warning("Exception while parsing GPGSV trame : " + sTrame, False)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ CONVERSION @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    def set_gps_time(self, sTime):
        try:
            hms, millis = sTime.split('.')
            millis = int(millis)
            h = int(hms[:2])
            m = int(hms[2:4])
            s = int(hms[4:6])
            self.oCurrentFix.dtGPSDate.hour = h
            self.oCurrentFix.dtGPSDate.minute = m
            self.oCurrentFix.dtGPSDate.second = s
            self.oCurrentFix.dtGPSDate.microsecond = millis * 1000
        except:
            self.exception("Failed to parse GPS time : "+str(sTime))

    def set_gps_date(self, sDate):
        try:
            d = int(sDate[:2])
            mth = int(sDate[2:4])
            y = int(sDate[4:6])
            self.oCurrentFix.dtGPSDate.day = d
            self.oCurrentFix.dtGPSDate.month = mth
            self.oCurrentFix.dtGPSDate.year = y
        except:
            self.exception("Failed to parse GPS date: " + str(sDate))



#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ GPS FIX @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


class GPSFix():

    def __init__(self):
        # Validity
        self.bValid = False
        self.iPositionFixIndicator = -1 # 0 = No fix, 6 = dead reckoning, 1,2 = ok
        # Coordinates
        self.sLatitude = ""
        self.sNSIndicator = ""
        self.sLongitude = ""
        self.sEWIndicator = ""
        self.fHDOP = -1
        #Altitude
        self.fAltitudeMSL = -1
        self.fGeoid = -1
        # Dynamics
        self.fSpeedOverGround = -1# kph
        self.fCourseOverGround = -1 # degres
        # Time
        self.dtSystemDate = datetime.now()
        self.dtGPSDate = datetime.min
        # Sattelite Data
        self.iSatUsed = -1
        self.iSatInView = -1

    def log_str(self):
        sLog = "FixIndic : "+str(self.iPositionFixIndicator)+", Coordinatates : "+self.sLatitude+" "+self.sNSIndicator+" "+self.sLongitude+" "+self.sEWIndicator+", Precision : "+str(self.fHDOP)\
        +", Altitude : "+str(self.fAltitudeMSL)+"m MSL "+str(self.fGeoid)+"m Geoid, Speed :"+str(self.fSpeedOverGround)+"kph "+str(self.fCourseOverGround)+"°, System Date : "+str(self.dtSystemDate)\
        +" GPS Date : "+str(self.dtGPSDate)+", SatUsed : "+str(self.iSatUsed+" SatInView : "+str(self.iSatInView))




#@@@@@@@@@@@@@@@@@@@@@@@@@@@@ CONVIENT FUNCTIONS @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@



def knots_to_kph(self, fKnots):
    return fKnots * 1.852
