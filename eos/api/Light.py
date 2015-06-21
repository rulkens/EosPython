import numpy as np
import math

# ===========================================================================
# Light class
# provides an abstract light that can be positioned in some place on the lamp
# with some nice effects
# ===========================================================================

# generic light class
class Light:
    def __init__(self, position = 0.0, size = 1.0, intensity = 1.0, falloff_curve='linear', num_lights=32):
        self.position = position
        self.size = size
        self.intensity = intensity

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
        # apply the falloff curve
        values = map(lambda i: self._intensity_at(i), values)
        values = np.clip(values, 0, 1)

        total_intensity = sum(values)
        print('total %s' % total_intensity)
        # to do anti-alisaing, normalize the values towards the intensity
        # i.e. the total surface area under the curve is equal to the intensity
#         values = map(lambda i: self.intensity*i/total_intensity, values)
        # get total intensity
        print('values %s' % values)
        # return
        return values

    def _intensity_at(self, pos):
        """get the intensity of the light at a certain position"""
        distance = abs(pos - self.position)
        intensity = self.falloff_curves[self.falloff_curve](distance, self.size/2.0)
        return intensity * self.intensity

