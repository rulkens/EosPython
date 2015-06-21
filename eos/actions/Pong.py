import logging
import math
import numpy as np
import time
import logging

from Action import Action
from eos.api.Light import Light
from noise import pnoise2

# ===========================================================================
# Pong Action
#
# move a light up and down the EOS lamp
# ===========================================================================

FRAMERATE = 60.0
SLEEP_TIME = 1.0/FRAMERATE
NUM_LIGHTS = 32
LIGHTS_SEC = FRAMERATE * NUM_LIGHTS

class Pong(Action):
    def __init__(self, driver, **kwargs):
        self.driver = driver
        self._defaults(**kwargs)
        super(Pong, self).__init__()

    def _defaults(self, speed=2.0, direction=1):
        self.speed = speed
        self.direction = direction

        self.size = 3.0/NUM_LIGHTS # light size

        self.light = Light(size=self.size, falloff_curve='linear', intensity=0.4)

    def run(self):
        logging.info('Glow initialized - and ready to go!')
        while True:
            with self.state:
                if self.paused:
                    self.state.wait() # block until notified
            self.step()
            time.sleep(SLEEP_TIME)

    def step(self):
        self.light.position += self.direction*(self.speed/LIGHTS_SEC)

        if self.light.position > 1:
            self.direction = -1
        if self.light.position < 0:
            self.direction = 1

        self.driver.set(self.light.result())
        # TODO: send a message somewhere with the status