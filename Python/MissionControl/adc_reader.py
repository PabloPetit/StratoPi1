import RPi.GPIO as GPIO

#Read SPI data from MCP3008. 0<= adcnum < 8
def readadc(adcnum, clockpin, mosipin, misopin, cspin):

	if ((adcnum > 7) or (adcnum < 0)):
			return -1

	GPIO.output(cspin, True)
	GPIO.output(clockpin, False)  # start clock low
	GPIO.output(cspin, False)	 # bring CS low

	commandout = adcnum
	commandout |= 0x18  # start bit + single-ended bit
	commandout <<= 3	# we only need to send 5 bits here

	for i in range(5):

			if (commandout & 0x80):
					GPIO.output(mosipin, True)

			else:
					GPIO.output(mosipin, False)
			commandout <<= 1

			GPIO.output(clockpin, True)
			GPIO.output(clockpin, False)

	adcout = 0
	# read in one empty bit, one null bit and 10 ADC bits
	for i in range(12):

			GPIO.output(clockpin, True)
			GPIO.output(clockpin, False)
			adcout <<= 1

			if (GPIO.input(misopin)):
					adcout |= 0x1

	GPIO.output(cspin, True)
	adcout /= 2	   # first bit is 'null' so drop it

	return adcout


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

SPICLK = 23
SPIMISO = 21
SPIMOSI = 19
SPICS = 24
# definition de l'interface SPI
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)


adcnum = 7
# Lecture de la valeur brute du capteur
read_adc0 = readadc(adcnum, SPICLK, SPIMOSI, SPIMISO, SPICS)
# conversion de la valeur brute lue en milivolts = ADC * ( 3300 / 1024 )
millivolts = read_adc0 * ( 3300.0 / 1024.0)





















