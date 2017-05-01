from uart_module import *
import collections

class GPSModule(UartModule):

    def __init__(self, oMainLog):
        UartModule.__init__(self, oMainLog)

        self.name = GPS_NAME
        self.sLogPath = GPS_LOG_PATH
        self.fUpdateDelay = GPS_UPDATE_DELAY

        self.dqLastPositions = collections.deque(maxlen=GPS_MEMORY)
        self.dqLastAltitudes = collections.deque(maxlen=GPS_MEMORY)

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

    def create_command_states(self):
        pass

    def create_debuffer_dict(self):
        pass

    def check_self_integrity(self):
        pass

    def handle_no_integrity(self):
        pass

    def module_run(self):
        pass

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

        except Exception:
            self.warning("Exception while parsing GPRMC trame : "+sTrame)

    def read_GPVTG(self, sTrame):
        pass

    def read_GPGGA(self, sTrame):
        pass

    def read_GPGLL(self, sTrame):
        pass

    def read_GPGSA(self, sTrame):
        pass

    def read_GPGSV(self, sTrame):
        pass

    def convert_GPS_time_to_datetime(self, sTime):
        try:
            hms, millis = sTime.split('.')
            millis = int(millis)
            h = int(hms[:2])
            m = int(hms[2:4])
            s = int(hms[4:6])
            return datetime( self.dtInitDate.year, self.dtInitDate.month, self.dtInitDate.day, h, m, s, millis)
        except Exception:
            self.warning("Wrong GPS Time data")
            return datetime.min







