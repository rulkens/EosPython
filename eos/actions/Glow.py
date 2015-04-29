import logging
import math
import numpy as np
import time
import logging

from Action import Action
from noise import pnoise2

# ===========================================================================
# Glow Action
#
# this continually runs a glow animation on EOS
# - use Action methods pause() and resume() to control the action in time
#
# ===========================================================================

FRAMERATE = 60.0
SLEEP_TIME = 1.0/FRAMERATE
NUM_LIGHTS = 32

class Glow(Action):
    def __init__(self, driver, **kwargs):
        self.driver = driver
        self._defaults(**kwargs)
        super(Glow, self).__init__()

    def _defaults(self, speed=0.009, spacing=0.2, intensity=0.8, falloff=3.0, index_range=[0,31]):
        self.speed = speed
        self.spacing = spacing
        self.intensity = intensity
        self.falloff = falloff
        self.index_range = index_range

    def run(self):
        logging.info('Glow initialized - and ready to go!')
        self.x = 0.0
        while True:
            with self.state:
                if self.paused:
                    self.state.wait() # block until notified
            self.step()
            time.sleep(SLEEP_TIME)

    def step(self):
        self.driver.set(vals_in_time(self.x, self.speed, self.spacing, self.intensity, self.falloff, self.index_range))
        self.x += 1.0
        # TODO: send a message somewhere with the status


def vals_in_time(time, speed, spacing, intensity, falloff, index_range):
    """calculate all the values in time, x is time, y is position on the lamp"""
    vals = [noise(time,y,speed,spacing, intensity,falloff) for y in range(0,NUM_LIGHTS)]
    # logging.info('glowing %s' % vals)
    # turn off lights that are not in the range
    for i in range(0,index_range[0]):
        vals[i] = 0
    for i in range(index_range[1], NUM_LIGHTS):
        vals[i] = 0
    #         print(eos.status)
    logging.info('total intensity: %.4f | average intensity %.4f' % (sum(vals), np.mean(vals)))
    return vals

def noise(x, y, speed, spacing, intensity, falloff):
    """random noise generator, using perlin noise function"""
    basenoise = pnoise2(x*speed, y*spacing, octaves=2)+.4
    basenoise *= intensity
    return math.pow(basenoise, falloff)