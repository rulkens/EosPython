#!/usr/bin/python
from eos.driver.EOS_Driver import EOS_Driver
import time
import atexit

# ===========================================================================
# Example Code
# ===========================================================================

eos = EOS_Driver(debug=True)

def exitHandler():
    print 'Exiting!'
    eos.allOff()

atexit.register(exitHandler)

# define different functionality
def interactiveAll():
    newValue = raw_input('New value (0-4095): ')
    # convert to number
    intensity = int(float(newValue))
    eos.all(intensity)

def sweep(t = 1):
    print "sweeping the leds with a predefined time (%s sec)" % t
    for selected in range(0,32):
        eos.only(selected)
        time.sleep(t)

def blinkAll(t = 2):
    """blink all the lights at once"""
    print "blink all the leds at once with time (%s sec)" % t
    eos.allOn()
    time.sleep(t)
    eos.allOff()
    time.sleep(t)
    
def setAndSleep(intensity, sec):
    """set the intensity of all the lights and sleep for a time (in sec)"""
    print "[setAndSleep]"
    print "set lights to %s and sleep for %s sec" % (intensity, sec)
    eos.setAll(intensity)
    time.sleep(sec)
    
def progressiveIntensity(sec = 2, steps = 10):
    """increase the intensity of all lights progressively"""
    print "[progressiveIntensity]"
    for i in range(0, steps+1):
        intensity = float(i)/steps
        print "set light to intensity %s" % intensity
        eos.all(intensity)
        time.sleep(sec)

def progressiveIntensityOne(index = 0, sec = .1, steps = 10):
    """increase the intensity of one light progressively"""
    for i in range(0, steps+1):
        intensity = float(i)/steps
        print "setting light #%s to %s" % (index, intensity)
        eos.setOne(index, intensity)
        time.sleep(sec)

def blinkLight(light = 1, sec = 2):
    """blink a specific light for a set number of seconds"""
    eos.on(light)
    time.sleep(sec)
    eos.off(light)
    time.sleep(sec)

def blinkTest():
    blinkLight(1, .5)
    blinkLight(2)
    blinkLight(3, .5)
    blinkLight(4)
    blinkLight(5, .5)
    blinkLight(6)
    
def setSomeRandomValues():
    eos.set([0,0,0,1,0,0,.5,.3,.2,.1,0,0,0,1,0,1,0])

if __name__ == "__main__":
    # main program
    progressiveIntensity()
    progressiveIntensityOne(1)
    sweep()
    blinkTest()
    setSomeRandomValues()
    time.sleep(10)
    interactiveAll()