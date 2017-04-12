from threading import *
import queue
import time



class Module( Thread ):

    def __init__( self, oLock, fDelay ):

        Thread.__init__( self )

        self.oLock = oLock
        self.fDelay = fDelay
        self.bStop = False

    def run(self):

        while not self.stop_condition() :

            if not self.check_self_integrity():
                self.handle_no_integrity()
            else:
                self.module_run()
                self.log()
            time.sleep( self.delay )

    def stop_condition(self):
        return self.bStop

    def check_self_integrity(self):
        raise NotImplementedError("check_self_integrity not implemented")

    def handle_no_integrity(self):
        raise NotImplementedError("handle_no_integrity not implemented")

    def module_run(self):
        raise NotImplementedError("module_run not implemented")

    def log(self):
        raise NotImplementedError("log not implemented")








    """
    def manage_queue(self):
        try:
            func, args, kwargs = self.q.get(timeout=self.timeout)
            func(*args, **kwargs)
        except queue.Empty:
            pass
        except Exception:
            pass
        pass
         
    def on_thread(self, func, *args, **kwargs):
        self.q.put((func, args, kwargs))
    """




    class State:
        INITIALIZING = 5  # InitialState
        OPERATIONAL = 1  # Init done, functional test ok
        ASLEEP = 2  # Module Put to sleep waiting for awake
        NOT_RESPONDING = 3  # Module has not respond to last functional test
        RECONNECTING = 4
        DEAD = 5  # ... Mission failure