from uart_module import *
import collections

class GPSModule(UartModule):

    def __init__(self, oMainLog, sPort):
        UartModule.__init__(self, oMainLog, sPort)

        self.iBauds = GPS_BAUDS

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
        self.oRawHandler.setFormatter(ONLY_MESSAGE_LOG_FORMATTER)

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
            self.info(self.get_log_announcement_str()+self.oCurrentFix.log_str())

    def evaluate_module_ready(self):
        self.bIsReady = self.oLastFix is not None # If first correct fix is acquired

    def at_start(self):
        try:
            self.oSer.flush()
        except:
            self.exception("Could not flush GPS serial data at start")

    def module_run(self):
        try:
            self.set_buffer()
            if len(self.sLastBuffer) > 0:
                self.oCurrentFix = GPSFix()
                self.read_gps_data()
                self.validate_fix()
        except:
            self.exception("Could not read buffer from GPS UART device")


    def set_buffer(self):

        self.sLastBuffer = ""
        self.debug("Waiting for data ...")
        fTotalTime = 0
        while len(self.sLastBuffer) == 0 :
            time.sleep(GPS_BUFFER_READ_INTERVAL)
            fTotalTime += GPS_BUFFER_READ_INTERVAL
            self.sLastBuffer = self.read_buffer(True).decode("ascii")
            if fTotalTime >= GPS_MAX_WAIT_TIME:
                self.error("No data received")
                break

        while True:
            time.sleep(GPS_BUFFER_READ_INTERVAL)
            sTemp = self.read_buffer(True).decode("ascii")
            self.sLastBuffer += sTemp
            if len(sTemp) == 0:
                break

        self.debug("Buffer data received : "+str(len(self.sLastBuffer)))


    def validate_fix(self):

        if self.oCurrentFix is not None and self.oCurrentFix.bValid and self.oCurrentFix.iPositionFixIndicator > 0:
            self.oLastFix = self.oCurrentFix
            self.dqFixMemory.appendleft(self.oCurrentFix)
            self.info("Fix validated : \n"+self.oLastFix.log_str())
        else:
            if self.oCurrentFix is None:
                self.info("Fix not validate : Current fix is None")
            else:
                self.info("Fix not validated : is Valid : "+str(self.oCurrentFix.bValid)+", Indicator : "+str(self.oCurrentFix.iPositionFixIndicator))


    def read_gps_data(self):
        try:
            self.info("Reading GPS data : ")
            self.debug("\n"+self.sLastBuffer)
            for trame in self.sLastBuffer.split("\r\n"):
                try:
                    sPrefixe = trame.split(",")[0].replace('$','')
                    if len(sPrefixe) > 0:
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
                self.oCurrentFix.fAltitudeMSL = float(lValues[9])
                self.oCurrentFix.fGeoid = float(lValues[11])
            except:
                self.oCurrentFix.bValid = False
                self.warning("Could not read GGA important number info ( Fix indicator, MSL, Geoid )", False)
            try:
                self.oCurrentFix.iSatUsed = int(lValues[7])
            except:
                self.info("Could not read GGA SatUsed")

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
                self.info("No data for speed over ground or course over ground", False)
        except Exception:
            self.exception("Exception while parsing GPRMC trame : "+sTrame, False)

    def read_GPVTG(self, sTrame):
        pass

    def read_GPGLL(self, sTrame):
        pass

    def read_GPGSA(self, sTrame):
        try:
            lValues = sTrame.split(',')
            try:
                self.oCurrentFix.fPDOP = float(lValues[15])
                self.oCurrentFix.fHDOP = float(lValues[16])
                self.oCurrentFix.fVDOP = float(lValues[17].split('*')[0])
            except:
                self.info("No data for PDOP, HDOP or VDOP : "+sTrame)
        except:
            self.exception("Exception while parsing GPGSA trame : " + sTrame, False)

    def read_GPGSV(self, sTrame):
        try:
            lValues = sTrame.split(',')
            try:
                self.oCurrentFix.iSatInView = int(lValues[3])
            except:
                self.info("No data for sattelites in view : ")
        except:
            self.exception("Exception while parsing GPGSV trame : " + sTrame, False)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ CONVERSION @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    def set_gps_time(self, sTime):
        try:
            if len(sTime) > 8: # TODO check if 8 is a good value
                hms, millis = sTime.split('.')
                micro = int(millis) * 1000
                h = int(hms[:2])
                m = int(hms[2:4])
                s = int(hms[4:6])
                self.oCurrentFix.dtGPSDate = self.oCurrentFix.dtGPSDate.replace(hour=h)
                self.oCurrentFix.dtGPSDate = self.oCurrentFix.dtGPSDate.replace(minute=m)
                self.oCurrentFix.dtGPSDate = self.oCurrentFix.dtGPSDate.replace(second=s)
                self.oCurrentFix.dtGPSDate = self.oCurrentFix.dtGPSDate.replace(microsecond=micro)
        except:
            self.exception("Failed to parse GPS time : "+str(sTime))

    def set_gps_date(self, sDate):
        try:
            if len(sDate) == 6:
                d = int(sDate[:2])
                mth = int(sDate[2:4])
                y = int(sDate[4:6]) + 2000
                self.oCurrentFix.dtGPSDate = self.oCurrentFix.dtGPSDate.replace(year=y)
                self.oCurrentFix.dtGPSDate = self.oCurrentFix.dtGPSDate.replace(month=mth)
                self.oCurrentFix.dtGPSDate = self.oCurrentFix.dtGPSDate.replace(day=d)
        except:
            self.exception("Failed to parse GPS date: " + str(sDate))



#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ GPS FIX @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


class GPSFix():

    def __init__(self):
        # Validity
        self.bValid = True
        self.iPositionFixIndicator = -1 # 0 = No fix, 6 = dead reckoning, 1,2 = ok
        # Coordinates
        self.sLatitude = ""
        self.sNSIndicator = ""
        self.sLongitude = ""
        self.sEWIndicator = ""
        self.fPDOP = -1
        self.fHDOP = -1
        self.fVDOP = -1
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
        sLog = "FixIndic "+str(self.iPositionFixIndicator)+", Coords "+self.sLatitude+" "+self.sNSIndicator+" "+self.sLongitude+" "+self.sEWIndicator+", PDOP, HDOP, VDOP "+str(round(self.fPDOP, 2))\
        +" "+str(round(self.fHDOP, 2))+" "+str(round(self.fVDOP, 2))+", AltMSL "+str(self.fAltitudeMSL)+"m Geo : "+str(self.fGeoid)+"m, Speed : "+str(round(self.fSpeedOverGround, 2))+"kph "\
        +str(round(self.fCourseOverGround, 2))+"°, SysDt "+str(self.dtSystemDate)+" GPSDt "+str(self.dtGPSDate)+", SatUsed "+str(self.iSatUsed)+" SatInView "+str(self.iSatInView)
        return sLog




#@@@@@@@@@@@@@@@@@@@@@@@@@@@@ CONVIENT FUNCTIONS @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@



def knots_to_kph(fKnots):
    return fKnots * 1.852
