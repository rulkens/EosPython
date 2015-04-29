import threading
import logging

# ===========================================================================
# Action
#
# a generic object that defines an action to take on the EOS lamp. It is
# executed in a separate thread, allowing animation and other fancy effects.
#
# To use: create a new Action object, then call the `start()` method, then
# use `pause()` and `resume()` to control execution
#
# TODO: define more higher level functions of actions:
# - fadein / fadeout effects
# - feedback messages with current status
# - timing: execute the action at a certain time in the day (bit like crontab?)
# ===========================================================================

class Action(threading.Thread):
    """Thread class with a resume() and pause() method. The thread itself has to check
    regularly for the self.state condition."""
    def __init__(self):
        threading.Thread.__init__(self)
        self.iterations = 0
        self.daemon = True  # OK for main to exit even if instance is still running
        self.paused = True  # start out paused
        self.state = threading.Condition()

    def run(self):
        """start the action. This method is called when thread.start() is called"""
        while True:
            with self.state:
                if self.paused:
                    self.state.wait() # block until notified
            time.sleep(1)
            logging.info('Action executed!')

    def resume(self):
        """resume executing in this action"""
        logging.info('Resuming action executing')
        with self.state:
            self.paused = False
            self.state.notify()  # unblock self if waiting

    def pause(self):
        """pause execution"""
        logging.info('Pausing action executing')
        with self.state:
            self.paused = True  # make self block and wait