
from gsm_module import *
import time


def test():
    pass

print(test)

gsm = GsmModule(1)
gsm.open_serial()
gsm.start()

time.sleep(3)

print(gsm.dCommandStates[AT_STATE].iState)