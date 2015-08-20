import numpy as np
import math
import colorsys

# ===========================================================================
# Color Light class
# provides an abstract light that can be positioned in some place on the lamp
# with some nice effects, and with a color.
# ===========================================================================

# generic light class
class ColorLight:
    def __init__(self, position = 0.0, size = 1.0, intensity = 1.0, color = 0xFFFFFF, falloff_curve='linear', num_lights=120):
        self.position = position
        self.size = size
        self.intensity = intensity
        self.color = int(color, base=0)

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

        b = float(self.color & 0xFF) / 0xFF
        g = float((self.color >> 8) & 0xFF) / 0xFF
        r = float((self.color >> 16) & 0xFF) / 0xFF
        # compute the color
        self.rgb = (r,g,b)
        self.hls = colorsys.rgb_to_hls(self.rgb[0], self.rgb[1], self.rgb[2])

        print self.rgb

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
        intensity = np.clip(intensity, 0, 1) * self.intensity
        print "intensity %s" % intensity
        color = hls_to_color(self.hls[0], self.hls[1] * intensity, self.hls[2])
        print "color %s %s" % (pos, hex(color))
        return color

def hls_to_color(h, l, s):
    """convert hls to an integer color"""
    col = colorsys.hls_to_rgb(h, l, s)
    print col
    r = int(col[0] * 0xFF)
    g = int(col[1] * 0xFF)
    b = int(col[2] * 0xFF)
    #print "r %s g %s b %s" % (r, g, b)
    return (r << 16) + (g << 8) + b
