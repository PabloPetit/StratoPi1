from uart_module import *
import collections

class GPSModule(UartModule):

    def __init__(self, oMainLog, sPort):
        UartModule.__init__(self, oMainLog, sPort)

        self.name = GPS_NAME
        self.sLogPath = GPS_LOG_PATH
        self.fUpdateDelay = GPS_UPDATE_DELAY

        self.dqLastPositions = collections.deque(maxlen=GPS_MEMORY)
        self.dqLastAltitudes = collections.deque(maxlen=GPS_MEMORY) # [ MSL, GEO, DATE ]
        self.dqLastCoursesOverGround = collections.deque(maxlen=GPS_MEMORY)

        self.fMaxAltitude = 0.0

        self.bOnDescent = False

        self.dTramePref = {
            GPRMC : self.read_GPRMC,
            GPVTG : self.read_GPVTG,
            GPGGA : self.read_GPGGA,
            GPGLL : self.read_GPGLL,
            GPGSA : self.read_GPGSA,
            GPGSV : self.read_GPGSV
        }


    def setup(self):
        super(GPSModule, self).setup()

    def create_peridical_checks(self):
        pass

    def create_debuffer_dict(self):
        pass

    def check_self_integrity(self):
        return True

    def handle_no_integrity(self):
        pass

    def send_raw_log(self):
        pass

    def module_run(self):
        self.read_gps_data()

    def read_gps_data(self):
        try:
            sBuffer = self.read_buffer()
            for trame in sBuffer.split("\r\n"):
                try:
                    sPrefixe = trame.split("\r\n")[0].replace('$','')
                    self.dTramePref[sPrefixe](trame)
                except Exception:
                    self.warning("Wrong Prefixe on GPS trame parsing")
        except Exception:
            self.error("Exception while reading GPS data")

    def read_GPRMC(self, sTrame):
        try:
            lValues = sTrame.split(',')
            dtDate = self.convert_GPS_time_to_datetime(lValues[1], lValues[9])

            bDataValid = lValues[2] == 'A'
            sLatitude = lValues[3]
            sNSIndicator = lValues[4]
            sLongitude = lValues[5]
            sEWIndicator = lValues[6]

            self.record_position(sLatitude, sNSIndicator, sLongitude, sEWIndicator, bDataValid)

            try:
                fSpeedOverGround = self.knots_to_kph(float(lValues[7])) # kph
                fCourseOverGround = float(lValues[8]) # degres
                self.record_course( fSpeedOverGround, fCourseOverGround )
            except:
                self.debug("No data for speed over ground or course over ground")


        except Exception:
            self.warning("Exception while parsing GPRMC trame : "+sTrame, False)

    def read_GPVTG(self, sTrame):
        pass

    def read_GPGGA(self, sTrame):
        try:
            lValues = sTrame.split(',')

            sLatitude = lValues[2]
            sNSIndicator = lValues[3]
            sLongitude = lValues[4]
            sEWIndicator = lValues[5]

            self.record_position(sLatitude, sNSIndicator, sLongitude, sEWIndicator)

        except:
            self.warning("Exception while parsing GPGGA trame : " + sTrame, False)

    def read_GPGLL(self, sTrame):
        pass

    def read_GPGSA(self, sTrame):
        pass

    def read_GPGSV(self, sTrame):
        pass

    def record_position(self, sLatitude, sNS, sLongitude, sEW, bValid = True):
        if not bValid or sLatitude == "" or sNS == "" or sLongitude == "" or sEW == "":
            return

        sPos = sLatitude+','+sNS+','+sLongitude+','+sEW
        self.dqLastPositions.appendleft([sPos, datetime.now()])

    def record_course(self, fSpeed, fCourse):
        # Check for invalid data
        lData = [fSpeed, fCourse, datetime.now()]
        self.dqLastCoursesOverGround.appendleft(lData)

    def record_altitude(self, fMSL, fGeoid):
        pass


    def convert_GPS_time_to_datetime(self, sTime, sDate):
        try:
            hms, millis = sTime.split('.')
            millis = int(millis)
            h = int(hms[:2])
            m = int(hms[2:4])
            s = int(hms[4:6])

            d = int(sDate[:2])
            mth = int(sDate[2:4])
            y = int(sDate[4:6])

            return datetime( y, mth, d, h, m, s, millis)

        except Exception:
            self.warning("Wrong GPS Time data")
            return datetime.min

    def knots_to_kph(self, fKnots):
        return fKnots * 1.852







