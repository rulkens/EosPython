#!/usr/bin/python

from dotstar import Adafruit_DotStar
import math

# ===========================================================================
# Eos LED Driver Class - quite the low-level API
#
# the code assumes we have a dotstar LED array (APA102) with 120 LEDS connected
# to the
# hardware SPI (SPI0_SCLK - pin 23, SPI0_MOSI - pin 19)
#
# this driver is able to
#       - control the lights using the DotStar Driver
#       - provide intuitive control over the individual lamps as well
#         as low-level access to the PWM API
#
# lights are arranged from bottom (index = 0) to top (index = 119)
#
# TODO: convert from RBG to RGB
# ===========================================================================

# main Driver class
class EOS_LEDDriver:

    # CONSTANTS

    NUM_LIGHTS          = 120   # total number of lights

    PWM_MIN				= 0
    PWM_MAX				= 255
    PWM_ON				= 0xFFFFFF
    PWM_OFF				= 0

    LIGHT_ON            = 1     # normalized value for light that is on
    LIGHT_OFF           = 0     # normalized value for light that is off

    def __init__(self, debug=False, brightness=1.0, gamma=1.0):
        self.debug = debug

        # Initialise the PWM devices using the default address
        if self.debug: print "Initializing the driver"
        self.driver = Adafruit_DotStar(self.NUM_LIGHTS+1)
        self.driver.begin()

        self.setBrightness(brightness)
        self.setGamma(gamma)

        # reset the driver boards to turn all lights off
        # TODO: probably don't do this, and let the user decide
        # however, we won't have a status of the lights after the
        # app closes
        if self.debug: print "Turning all lights off"
        self.allOff()

    def allOff(self):
        """turn all the lights off"""
        for index in range(0, self.NUM_LIGHTS + 1):
            self.driver.setPixelColor(index, self.PWM_OFF)

        self.driver.clear()
        self.driver.show()
        self.status = [0.0] * self.NUM_LIGHTS  # update status
        return self.status

    def allOn(self):
        """turn all the lights on to maximum intensity"""
        for index in range(0, self.NUM_LIGHTS + 1):
            self.driver.setPixelColor(index, self.PWM_ON)
        self.driver.show()
        self.status = [1.0] * self.NUM_LIGHTS  # update status
        return self.status

    def one(self, index, color):
        """set a specific light to a normalized value intensity tuple with 3 values (0-1, 0-1, 0-1)"""
        # TODO: set light
        self.driver.setPixelColor(index, self.__rgbToRbg(color))
        # and show it
        self.driver.show()
        self.status[index] = color  # update status
        return self.status

    def oneRaw(self, index, color):
        """set a specific light to a color value (0-0xFFFFFF)"""
        self.driver.setPixelColor(index, self.__rgbToRbg(color))
        self.driver.show()
        self.status[index] = value  # update status
        return self.status

    def set(self, values):
        """set all lights to the value in the list provided"""
        for index, value in enumerate(values):
            # TODO: convert from normalized to absolute color
            # [0-1, 0-1, 0-1]
            self.driver.setPixelColor(index, self.__rgbToRbg(color))
        self.driver.show()
        self.status = values
        return self.status

    def setRaw(self, values):
        """set all leds to the raw (0xRRGGBB) value in the list provided"""
        for index, value in enumerate(values):
            self.driver.setPixelColor(index, self.__rgbToRbg(color))
        self.driver.show()
        return self.status

    def all(self, color):
        """set all lights to a specific normalized value intensity (0-1)"""
        for index in range(0, self.NUM_LIGHTS):
            self.driver.setPixelColor(index, self.__rgbToRbg(color))
        self.driver.show()
        self.status = [color] * self.NUM_LIGHTS  # update status
        return self.status

    def only(self, index, color = 1):
        """turn on only the specific light, and turn all other lights off"""
        for i in range(0, self.NUM_LIGHTS):
            self.driver.setPixelColor(index, self.__rgbToRbg(color) if index == i else self.LIGHT_OFF)
        self.driver.show()
        return self.status

    def on(self, index):
        """turn the light with specific index on (to maximum value)"""
        return self.one(index, self.LIGHT_ON)

    def off(self, index):
        """turn the light with specific index off"""
        return self.one(index, self.LIGHT_OFF)

    def setFreq(self, freq):
        """set the PWM frequency (in Hz)"""
        # TODO: this is a function of the DotStar leds, but don't know how to use it

    def getStatus(self):
        """get the status of the lights as a list"""
        return self.status

    def setBrightness(self, brightness=1.0):
        """set the normalized brightness of all the leds"""
        self.brightness = int(brightness * self.PWM_MAX) # normalize
        self.driver.setBrightness(self.brightness)

    def setGamma(self, gamma=1.0):
        """set the gamma, gets used next time a led is set"""
        self.gamma = gamma

    # PRIVATE METHODS
    def __getLightIndex(self, index):
        """get the physical index and index of the boards for the specific light"""
        return index

    def __getAbsValue(self, value):
        """get absolute integer value (0-PWM_MAX) from a normalized (0-1) value"""
        # gamma correction
        val = math.pow(value, self.gamma)
        # return the clamped version
        return int(max(self.PWM_MIN, min(self.PWM_MAX, val*self.PWM_MAX)))

    def __rgbToRbg(self, color):
    	"""convert a color from RGB to RBG"""
    	r = (color >> 16) & 0xFF
    	g = (color >> 8) & 0xFF
    	b = (color) & 0xFF
    	rbg = (r << 16) + (b << 8) + g
    	# print "%s %s %s" % (r,g,b)
    	return rbg

    def __rbgToRgb(self, color):
    	"""convert a color from RBG to RGB"""
    	r = (color >> 16) & 0xFF
    	g = (color) & 0xFF
    	b = (color >> 8) & 0xFF
    	rgb = (r << 16) + (g << 8) + b
    	# print "%s %s %s" % (r,g,b)
    	return rgb
