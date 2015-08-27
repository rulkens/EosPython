import numpy as np
import math
import colorsys

import eos.api.colorutil as cutil

# ===========================================================================
# Color Light class
# provides an abstract light that can be positioned in some place on the lamp
# with some nice effects, and with a color.
# ===========================================================================

# generic light class
class ColorLight:
    def __init__(self, position = 0.0, size = 10.0, intensity = 1.0, color = 0xFFFFFF, falloff_curve='quad', num_lights=120):
        self.position = position
        self.size = size
        self.intensity = intensity
        # support hex definitions
        try:
            self.color = int(color, 0)
        except TypeError:
            self.color = int(color)
            print 'color %s' % self.color

        self.falloff_curve = falloff_curve
        self.num_lights = num_lights

        self.falloff_curves = {
            'linear': lambda dist, size: 1-abs(dist/size),   # a triangular falloff curve
            'quad':   lambda dist, size: 1-math.pow(abs(dist/size),2),
            'cube':   lambda dist, size: 1-math.pow(abs(dist/size),3)
        }


    def result(self):
        # calculate all the intensities
        values = [ float(i)/(self.num_lights-1) for i in range(0, self.num_lights)]

        # clip intensities
        values = np.clip(values, 0, 1)

        self.rgb = cutil.color_to_rgb(self.color)
        self.hls = cutil.color_to_hls(self.color)

        print 'hls'
        print self.hls

        # apply the falloff curve
        values = map(lambda i: self._color_at(i), values)
        # values = np.clip(values, 0, 1)

        print('values %s' % values)
        # return
        return values

    def _color_at(self, pos):
        """get the intensity of the light at a certain position"""
        distance = abs(pos - self.position)
        intensity = self.falloff_curves[self.falloff_curve](distance, self.size/2.0)
        print "intensity %s" % intensity
        intensity = np.clip(intensity, 0, 1) * self.intensity

        color = cutil.hls_to_color((self.hls[0], self.hls[1] * intensity, self.hls[2]))
        print "color %s %s" % (pos, hex(color))
        return color
