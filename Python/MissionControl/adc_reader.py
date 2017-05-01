import RPi.GPIO as GPIO
import time
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



print('Reading MCP3008 values, press Ctrl-C to quit...')
# Print nice channel column headers.
print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*range(8)))
print('-' * 57)
# Main program loop.
while True:
    # Read all the ADC channel values in a list.
    values = [0]*8
    for i in range(8):
        # The read_adc function will get the value of the specified channel (0-7).
        values[i] = readadc(i, SPICLK, SPIMOSI, SPIMISO, SPICS)
    # Print the ADC values.
    print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
    # Pause for half a second.
    time.sleep(0.5)




















