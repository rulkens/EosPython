from lib.Eos_Driver import EOS_Driver
from noise import pnoise2
import random, time, math
import numpy as np

# ===========================================================================
# Simplified EOS api
# ===========================================================================

# create the Eos_Driver object
eos = EOS_Driver()

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

def glow(opts):

    def noise(x, y):
        basenoise = pnoise2(x*0.003, y*0.2, octaves=2)+.3
        basenoise *= 0.8
        return math.pow(basenoise, 3)

    # TODO: define active region
    start = 2
    end = 25

    x = 0
    while True:
        vals = [ noise(x, y) for y in range(0,32)]
        # determine what part should be illuminated
        for i in range(0,start):
            vals[i] = 0
        for i in range(end, 32):
            vals[i] = 0

        eos.set(vals)
#         print(eos.status)
        print('total intensity: %.4f | average intensity %.4f' % (sum(vals), np.mean(vals)))
        time.sleep(.03)
        x = x + 1

# def glow2(opts):


def setFreq(opts):
    eos.setFreq(int(opts[0]))
    return "setting a new frequency to " % opts[0]

def status(opts):
    return eos.getStatus()

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

    'setfreq':      setFreq,
    'status':       status,
}

def errorHandler():
    print "the action cannot be found"

# export function
def EOS_API(action, args=None):
    print args
    return {'result': actions.get(action, errorHandler)(args), 'status': eos.getStatus() }

