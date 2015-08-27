import threading
import random
import time
import math
import numpy as np

from eos.driver.EOS_Driver import EOS_Driver
from eos.driver.EOS_LEDDriver import EOS_LEDDriver

from eos.actions.Glow import Glow
from eos.actions.Pong import Pong
from eos.actions.BinaryClock import BinaryClock

from Light import Light
from ColorLight import ColorLight

import eos.api.colorutil as cutil

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
eos_led = EOS_LEDDriver()

FRAMERATE = 60
NUM_HALOGEN_LIGHTS = eos.NUM_LIGHTS
NUM_LED_LIGHTS = eos_led.NUM_LIGHTS

# some constants
SLEEP_TIME = 1/FRAMERATE
LIGHTS_SEC = FRAMERATE * NUM_HALOGEN_LIGHTS

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

def setRaw(opts):
    eos.setRaw(opts)
    return "lights raw set to" % opts

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
glower.start() # start the glower thread (should probably only do this when it's actually needed...)
def glow(opts):
    if opts[0] == 'off':
        glower.pause()
        allOff([])
    if opts[0] == 'on':
        glower.resume()

## TODO: move to a separate file
ponger = Pong(eos)
ponger.start()
def pong(opts):
    if opts[0] == 'off':
        ponger.pause()
        allOff([])
    if opts[0] == 'on':
        ponger.resume()

## TODO: move to a separate file
clocker = BinaryClock(eos)
clocker.start()
def clock(opts):
    if opts[0] == 'off':
        clocker.pause()
        allOff([])
    if opts[0] == 'on':
        clocker.resume()

def light(opts):
    size = float(opts[1])/NUM_HALOGEN_LIGHTS # light size
    light = Light(size=size, intensity=float(opts[2]), falloff_curve=opts[3])
    light.position = float(opts[0])
    # set the actual light
    return eos.set(light.result())


## LED FUNCTIONALITY

def color_allOff(opts):
    eos_led.allOff()
    return "all LEDs turned off"

def color_allOn(opts):
    eos_led.allOn()
    return "all LEDs turned on"

def color_one(opts):
    eos_led.one(int(opts[0]), int(opts[1]))
    return "LEDs %s turned to intensity %s" % (opts[0], opts[1])

def color_set(opts):
    # convert opts to a list of floats
    eos_led.set(map(lambda o: int(o), opts))
    return "LED set to" % opts

def color_all(opts):
    eos_led.all(float(opts[0]))
    return "set all LEDs to intensity %s" % opts[0]

def color_only(opts):
    eos_led.only(int(opts[0]), int(opts[1]))
    return "turn on only light %s to intensity %s" % (opts[0],opts[1])

def color_on(opts=None):
    """ 0: index of light to turn fully on """
    if opts != None and opts != []:
        eos_led.on(int(opts[0]))
        return "light %s turned on" % opts[0]
    else:
        eos_led.allOn()
        return "all LEDs turned on"

def color_off(opts=None):
    if opts != None and opts != []:
        eos_led.off(int(opts[0]))
        return "LED %s turned off" % opts[0]
    else:
        eos_led.allOff()
        return "all LEDs turned off"


def color_light(opts):
    o           = OptList(opts)
    position    = o.get(0)
    color       = o.get(1)
    intensity   = o.get(2, 1.0)
    size        = o.get(3, 10.0)
    falloff_curve = o.get(4, 'linear')

    size = float(size)/NUM_LED_LIGHTS # light size
    light = ColorLight(size=size, intensity=float(intensity), falloff_curve=falloff_curve, color=color)
    light.position = float(position)
    # set the actual light
    return eos_led.set(light.result())

def color_gradient(opts):
    """color gradient"""
    o = OptList(opts)
    color1 = int(o.get(0))
    color2 = int(o.get(1))
    colorspace = o.get(2, 'hsv')

    vals = cutil.gradient(NUM_LED_LIGHTS, color1, color2, colorspace=colorspace)
    return eos_led.set(vals)

def color_gradients(opts):
    """multiple color gradients"""
    ## example: color_gradients 0 0xFF .5 0x0 1 0xFF
    ## even arguments are locations (low to high), odd arguments are color values
    gradients = reduce(cutil.opts_to_gradients, opts)


# overview of all the actions possible
actions = {
    'alloff':       allOff,
    'allon':        allOn,
    'one':          one,
    'set':          set,
    'setraw':       setRaw,
    'all':          all,
    'only':         only,
    'on':           on,
    'off':          off,

    'light':        light,

    # time-actions
    'glow':         glow,
    'pong':         pong,
    'clock':        clock,

    'setfreq':      setFreq,
    'status':       status,
    'gamma':        gamma,

    # LED actions
    'color_light':        color_light,
    'color_alloff':       color_allOff,
    'color_allon':        color_allOn,
    'color_one':          color_one,
    'color_set':          color_set,
    'color_all':          color_all,
    'color_only':         color_only,
    'color_on':           color_on,
    'color_off':          color_off,
    'color_gradient':     color_gradient

}

# simple option list class with default
class OptList(list):
    def get(self, index, default=None):
        return self[index] if len(self) > index else default

def errorHandler(error):
    print "the action cannot be run, error: %s" % error

# export function
def EOS_API(action, args=None):
    return {'result': actions.get(action, errorHandler)(args), 'status': eos.getStatus() }
