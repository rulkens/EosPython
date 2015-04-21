import logging
import math
import numpy as np
import logging
from datetime import datetime, time
import time as t
from Action import Action

# ===========================================================================
# BinaryClock Action
#
# this continually runs a clock animation that shows the time in binary
#
# ===========================================================================

FRAMERATE = 1.0
SLEEP_TIME = 1.0/FRAMERATE
NUM_LIGHTS = 32

class BinaryClock(Action):
    def __init__(self, driver, **kwargs):
        self.driver = driver
        super(BinaryClock, self).__init__()

    def run(self):
        logging.info('BinaryClock initialized')
        while True:
            with self.state:
                if self.paused:
                    self.state.wait() # block until notified
            self.step()
            t.sleep(SLEEP_TIME)

    def step(self):
        self.driver.set(vals_in_time())
        # TODO: send a message somewhere with the status

def vals_in_time():
    """returns a list of values for the current time"""
    seconds = seconds_since_midnight()
    # convert the number to binary, pad it and reverse it
    seconds_bin = '{:032b}'.format(seconds)[::-1]
    print seconds_bin
    vals = [float(seconds_bin[index]) for index in range(0,NUM_LIGHTS)]
    logging.info(vals)
    return vals

def seconds_since_midnight():
    """from http://stackoverflow.com/questions/8072740/number-of-seconds-since-the-beginning-of-the-day-utc-timezone"""
    utcnow = datetime.utcnow()
    midnight_utc = datetime.combine(utcnow.date(), time(0))
    delta = utcnow - midnight_utc
    return delta.seconds # <-- careful