from lib.driver.EOS_Driver import EOS_Driver
from Light import Light
from lib.actions.Glow import Glow

from noise import pnoise2
import random, time, math
import numpy as np

# ===========================================================================
# Higher level EOS api
#
# TODO:
# provide a set of actions that can be taken on the EOS lamp. An action can be
# instant, synchronous or asynchronous
# Then can also be timed (using crontab)
#
#
# ===========================================================================

# create the Eos_Driver object
eos = EOS_Driver()

FRAMERATE = 60
NUM_LIGHTS = eos.NUM_LIGHTS

# some constants
SLEEP_TIME = 1/FRAMERATE
LIGHTS_SEC = FRAMERATE * NUM_LIGHTS

# functions
def allOff(opts):
    eos.allOff()
    return "all lights turned off"

def allOn(opts):
    eos.allOn()
    return "all lights turned on"

def one(opts):
    eos.one(int(opts[0]), float(opts[1]))
    return "light %s turned to intensity %s" % (opts[0], opts[1])

def set(opts):
    # convert opts to a list of floats
    eos.set(map(lambda o: float(o), opts))
    return "lights set to" % opts

def all(opts):
    eos.all(float(opts[0]))
    return "set all lights to intensity %s" % opts[0]

def only(opts):
    eos.only(int(opts[0]), float(opts[1]))
    return "turn on only light %s to intensity %s" % (opts[0],opts[1])

def on(opts=None):
    """ 0: index of light to turn fully on """
    if opts != None and opts != []:
        eos.on(int(opts[0]))
        return "light %s turned on" % opts[0]
    else:
        eos.allOn()
        return "all lights turned on"

def off(opts=None):
    if opts != None and opts != []:
        eos.off(int(opts[0]))
        return "light %s turned off" % opts[0]
    else:
        eos.allOff()
        return "all lights turned off"

def setFreq(opts):
    eos.setFreq(int(opts[0]))
    return "setting a new frequency to " % opts[0]

def status(opts):
    return eos.getStatus()

def gamma(opts):
    return eos.setGamma(float(opts[0]))

## HIGHER-LEVEL functionality

## TODO: move to a separate file
glower = Glow(eos)
def glow(opts):
    print glow.driver
    if opts[0] is 'off':
        glower.stop()
    else:
        glower.start()


## TODO: move to a separate file
# def glow2(opts):
def pong(opts):

    size = 3.0/NUM_LIGHTS # light size
    speed = 7.0 # in lights/sec


    light = Light(eos, size=size, falloff_curve='quad', intensity=1)

    print('position %s' % light.position)

    direction = 1

    # move the light up and down the tube
    while True:
        light.position += direction*(speed/LIGHTS_SEC)

        eos.set(light.result())

        time.sleep(SLEEP_TIME)
        if light.position > 1:
            direction = -1
        if light.position < 0:
            direction = 1

def light(opts):
    size = float(opts[1])/NUM_LIGHTS # light size
    light = Light(eos, size=size, intensity=float(opts[2]), falloff_curve=opts[3])
    light.position = float(opts[0])
    # set the actual light
    eos.set(light.result())

# overview of all the actions possible
actions = {
    'alloff':       allOff,
    'allon':        allOn,
    'one':          one,
    'set':          set,
    'all':          all,
    'only':         only,
    'on':           on,
    'off':          off,

    'glow':         glow,
    'pong':         pong,
    'light':        light,

    'setfreq':      setFreq,
    'status':       status,
    'gamma':        gamma
}

def errorHandler(error):
    print "the action cannot be run, error: %s" % error

# export function
def EOS_API(action, args=None):
    return {'result': actions.get(action, errorHandler)(args), 'status': eos.getStatus() }

