#!/usr/bin/python
from eos.driver.EOS_LEDDriver import EOS_LEDDriver

import time
import colorsys
import numpy as np
import math
from noise import pnoise2

driver = EOS_LEDDriver()
BETWEEN_TIME = 2.0 # seconds
NUM_LIGHTS = 120

def ledtest():
	hsl2()
	#driver.allOff()

	# primary_colors()
	# all_on_off()
	# primary_colors()
	# primary_colors_one()
	# secondary_colors_one()
	#
	# sweep_channel()

def primary_colors():


	#time.sleep(BETWEEN_TIME)
	#
	print "red"
	driver.all(0xFF0000)
	time.sleep(2)

	print "green"
	driver.all(0x00FF00)
	time.sleep(2)

	print "blue"
	driver.all(0x0000FF)
	time.sleep(2)

def all_on_off():
	print "all lights on"
	driver.allOn()
	time.sleep(BETWEEN_TIME)

	driver.all(0x050505)
	time.sleep(1.0)

	print "all lights off"
	driver.allOff()
	time.sleep(BETWEEN_TIME)

def primary_colors_one():
	# primary colors
	driver.allOff()
	driver.one(50, 0xFF0000)
	driver.one(54, 0x00FF00)
	driver.one(58, 0x0000FF)
	time.sleep(BETWEEN_TIME)

def secondary_colors_one():
	# secondary colors
	driver.allOff()
	driver.one(58, 0xFFFF00)
	driver.one(62, 0xFF00FF)
	driver.one(66, 0x00FFFF)
	time.sleep(BETWEEN_TIME)

	#time.sleep(1.0)

	#driver.one(40, 0xFF8833)

def hsl1():

	driver.allOff()

	for i in np.arange(0.01, 2.0, 0.01):
		for item in range(0,NUM_LIGHTS):
			h = float(item)/float(NUM_LIGHTS)
			driver.one(item, hls_to_rgb(math.pow(h, i), 0.5, 0.8))

		time.sleep(0.02)

def hsl2():
	driver.allOff()

	t = 0
	while True:
		for i in np.arange(0.0, 1.0, 0.01):
			for item in range(0,NUM_LIGHTS):
				h = float(item)/float(NUM_LIGHTS)
				driver.one(item, hls_to_rgb(i, math.pow(pnoise2(t*0.2, h*4, octaves=2), 2), h))

			time.sleep(0.02)
			t += 0.02


def sweep_channel():
	#time.sleep(0.5)
	# GREEN CHANNEL
	for index in range(0,driver.NUM_LIGHTS):
		val = int(255 * (float(index)/float(driver.NUM_LIGHTS)))
		driver.one(index, val & 0xFF)

	time.sleep(1)
	driver.allOff()


	for index in range(0,driver.NUM_LIGHTS):
		val = int(255 * (float(index)/float(driver.NUM_LIGHTS)))
		driver.one(index, val >> 8)

	time.sleep(1)
	driver.allOff()

	for index in range(0,driver.NUM_LIGHTS):
		val = int(255 * (float(index)/float(driver.NUM_LIGHTS)))
		driver.one(index, val >> 16)

	time.sleep(1)
	driver.allOff()


def one_by_one():

	print "Turn all lights on one by one"
	for index in range(0, driver.NUM_LIGHTS):
		driver.only(index, 0xFFFF00)
		time.sleep(BETWEEN_TIME/driver.NUM_LIGHTS*4)


# UTILITY FUNCTIONS
def hls_to_rgb(h, l, s):
	col = colorsys.hls_to_rgb(h, l, s)
	#print col
	r = int(col[0] * 255)
	g = int(col[1] * 255)
	b = int(col[2] * 255)
	#print "r %s g %s b %s" % (r, g, b)
	return (r << 16) + (g << 8) + b
