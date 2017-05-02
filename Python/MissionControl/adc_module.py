from module import *
import RPi.GPIO as GPIO

class ADCModule(Module):

    def __init__(self, oMainLog):
        Module.__init__(self, oMainLog)

        self.name = ADC_NAME
        self.sLogPath = ADC_LOG_PATH
        self.fUpdateDelay = ADC_UPDATE_DELAY
        self.tMainLogInterval = DEFAULT_MAIN_LOG_INTERVAL


    def setup(self):
        super(ADCModule, self).setup()
        # Be carreful to avoid conflicts with gpios
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        GPIO.setup(SPIMOSI, GPIO.OUT)
        GPIO.setup(SPIMISO, GPIO.IN)
        GPIO.setup(SPICLK, GPIO.OUT)
        GPIO.setup(SPICS, GPIO.OUT)


    def create_peridical_checks(self):
        self.dPeriodicalChecks[ADC_STATE] = ADCState(self.check_adc, ADC_REFRESH_TIMEOUT, ADC_STATE)

    def check_adc(self):

        iUv = self.read_adc(UV_ADC_PIN)
        iTempBattery = self.read_adc(TEMP_BATTERY_ADC_PIN)
        iTempOutside = self.read_adc(TEMP_OUTSIDE_ADC_PIN)

        lUv = [ iUv, self.get_mV(iUv)]
        lTempBattery = [iTempBattery, self.get_mV(iTempBattery), self.get_celsius(self.get_mV(iTempBattery))]
        lTempOutside = [iTempOutside, self.get_mV(iTempOutside), self.get_celsius(self.get_mV(iTempOutside))]

        oAdc_state = self.dPeriodicalChecks[ADC_STATE]
        oAdc_state.lUv = lUv
        oAdc_state.lTempBattery = lTempBattery
        oAdc_state.lTempOutside = lTempOutside



    def read_adc(self, pin_number): # Black Magic

        if pin_number > 7 or pin_number < 0:
            self.error("Wrong adc pin value : "+str(pin_number))
            return

        GPIO.output(SPICS, True)
        GPIO.output(SPICLK, False)
        GPIO.output(SPICS, False)

        iCommand_out = pin_number
        iCommand_out |= 0x18
        iCommand_out <<= 3

        for i in range(5):
            if (iCommand_out & 0x80):
                GPIO.output(SPIMOSI, True)
            else:
                GPIO.output(SPIMOSI, False)
            iCommand_out <<= 1

            GPIO.output(SPICLK, True)
            GPIO.output(SPICLK, False)

        iAdc_res = 0
        for i in range(12):

            GPIO.output(SPICLK, True)
            GPIO.output(SPICLK, False)
            iAdc_res <<= 1

            if (GPIO.input(SPIMISO)):
                iAdc_res |= 0x1

        GPIO.output(SPICS, True)
        iAdc_res /= 2

        return iAdc_res


    def get_mV(self, iAdc_res):
        return iAdc_res * ( 3300.0 / 1024.0 )

    def get_celsius(self, iMv):
        return ( iMv - 500.0 ) / 10.0

    def module_run(self):
        pass

    def check_self_integrity(self):
        return True

    def handle_no_integrity(self):
        pass

