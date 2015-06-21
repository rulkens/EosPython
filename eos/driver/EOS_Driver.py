#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import math

# ===========================================================================
# Eos Driver Class - quite the low-level API
#
# the code assumes we have two 12bit LED drivers, with I2C addresses 0x40 and 0x41
# <http://www.adafruit.com/products/815>
#
# TODO: be able to
#       - override the default addresses,
#       - set PWM frequency,
#       - detect which driver controls which lights,
#       - map the driver addresses to the physical light positions
#       - apply gamma correction
#
# lights are arranged from bottom (index = 0) to top (index = 31)
# ===========================================================================

# main Driver class
class EOS_Driver:

    # CONSTANTS
    PWM_FREQ            = 500    # PWM frequency
    PWM_DRIVER_ADDR1    = 0x40  # address of the first driver
    PWM_DRIVER_ADDR2    = 0x41  # address of the second driver

    PWM_ON              = 4095  # PWM value for fully on
    PWM_OFF             = 0     # PWM value for fully off
    PWM_MAX             = 4095  # maximum PWM value
    PWM_MIN             = 0     # minimum PWM value

    NUM_LIGHTS          = 32    # total number of lights

    LIGHT_ON            = 1     # normalized value for light that is on
    LIGHT_OFF           = 0     # normalized value for light that is off

    def __init__(self, freq=PWM_FREQ, debug=False, gamma=1.0):
        self.debug = debug
        self.gamma = gamma

        # Initialise the PWM devices using the default address
        if self.debug: print "Initializing the drivers on ports %s and %s" % (self.PWM_DRIVER_ADDR1, self.PWM_DRIVER_ADDR2)
        self.pwms = [ PWM(self.PWM_DRIVER_ADDR1), PWM(self.PWM_DRIVER_ADDR2) ]

        # Set PWM frequency to predefined Hz
        if self.debug: print "Set PWM frequency to %s" % freq
        self.setFreq(freq)

        # reset the driver boards to turn all lights off
        # TODO: probably don't do this, and let the user decide
        # however, we won't have a status of the lights after the
        # app closes
        if self.debug: print "Turning all lights off"
        self.allOff()

    def allOff(self):
        """turn all the lights off"""
        map(lambda pwm: pwm.setAllPWM(0,self.PWM_OFF), self.pwms)
        self.status = [0.0] * self.NUM_LIGHTS  # update status
        return self.status

    def allOn(self):
        """turn all the lights on to maximum intensity"""
        # map(lambda pwm: pwm.setAllPWM(0,PWM_ON), self.pwms)
        self.pwms[0].setAllPWM(0,self.PWM_ON)
        self.pwms[1].setAllPWM(0,self.PWM_ON)
        self.status = [1.0] * self.NUM_LIGHTS  # update status
        return self.status

    def one(self, index, value):
        """set a specific light to a normalized value intensity (0-1)"""
        light = self.__getLightIndex(index)
        val = self.__getAbsValue(value)
        self.pwms[light[0]].setPWM(light[1], 0, val)
        self.status[index] = value  # update status
        return self.status

    def oneRaw(self, index, value):
        light = self.__getLightIndex(index)
        self.pwms[light[0]].setPWM(light[1], 0, value)
        self.status[index] = value  # update status
        return self.status

    def set(self, values):
        """set all lights to the value in the list provided"""
        for index, value in enumerate(values):
            self.one(index, value)
        return self.status
        
    def setRaw(self, values):
        """set all lights to the raw (PWM) value in the list provided"""
        or index, value in enumerate(values):
            self.oneRaw(index, value)
        return self.status

    def all(self, value):
        """set all lights to a specific normalized value intensity (0-1)"""
        map(lambda pwm: pwm.setAllPWM(0,self.__getAbsValue(value)), self.pwms)
        self.status = [value] * self.NUM_LIGHTS  # update status
        return self.status

    def only(self, index, value = 1):
        """turn on only the specific light, and turn all other lights off"""
        for light in range(0,self.NUM_LIGHTS):
            self.one(light, value if index == light else self.LIGHT_OFF)
        return self.status

    def on(self, index):
        """turn the light with specific index on (to maximum value)"""
        return self.one(index, self.LIGHT_ON)

    def off(self, index):
        """turn the light with specific index off"""
        return self.one(index, self.LIGHT_OFF)

    def setFreq(self, freq):
        """set the PWM frequency (in Hz)"""
        map(lambda pwm: pwm.setPWMFreq(freq), self.pwms)

    def getStatus(self):
        """get the status of the lights as a list"""
        return self.status

    def setGamma(self, gamma=1.0):
        self.gamma = gamma
        # recalculate values
        return self.set(self.status)

    # PRIVATE METHODS
    def __getLightIndex(self, index):
        """get the physical index and index of the boards for the specific light"""
        even = index % 2 == 0
        physIndex = int(index / 2) # physical index
        return [0 if even else 1, physIndex if even else int(self.NUM_LIGHTS/2-1) - physIndex]

    def __getAbsValue(self, value):
        """get absolute integer value (0-PWM_MAX) from a normalized (0-1) value"""
        # gamma correction
        val = math.pow(value, self.gamma)
        # return the clamped version
        return int(max(self.PWM_MIN, min(self.PWM_MAX, val*self.PWM_MAX)))
