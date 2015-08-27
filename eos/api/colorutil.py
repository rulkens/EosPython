# color utility functions
import colorsys
from itertools import izip

def rgb_to_color(rgb):
    r = int(rgb[0] * 0xFF)
    g = int(rgb[1] * 0xFF)
    b = int(rgb[2] * 0xFF)
    #print "r %s g %s b %s" % (r, g, b)
    return (r << 16) + (g << 8) + b

def color_to_rgb(color):
    """from an integer to a normalized color triplet"""
    b = float(color & 0xFF) / 0xFF
    g = float((color >> 8) & 0xFF) / 0xFF
    r = float((color >> 16) & 0xFF) / 0xFF
    return (r, g, b)

def hls_to_color(hls):
    """convert hls to an integer color"""
    rgb = colorsys.hls_to_rgb(hls[0], hls[1], hls[2])
    return rgb_to_color(rgb)

def color_to_hls(color):
    """from an integer to hls"""
    rgb = color_to_rgb(color)
    return colorsys.rgb_to_hls(rgb[0], rgb[1], rgb[2])

def color_to_hsv(color):
    rgb = color_to_rgb(color)
    return colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])

def hsv_to_color(hsv):
    rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    return rgb_to_color(rgb)

def opts_to_gradients(opts, num_items):
    """ in pairs of 2, convert to (start_pos, end_pos, start_color, end_color)"""
    # the number of items

    grads = pairwise(opts)


def gradient(steps, start_color, end_color, colorspace='hsv'):
    """interpolate between start_color and end_color over some color space (hls, hsv, rgb)"""

    if colorspace == 'hsv':
        start_hsv = color_to_hsv(start_color)
        end_hsv = color_to_hsv(end_color)
        # use a list comprehension to build a list of interpolated hls values
        hsv_values = [transition3(i, steps, start_hsv, end_hsv) for i in range(0, steps)]
        rgb_values = map(hsv_to_color, hsv_values)

    if colorspace == 'hls':
        start_hls = color_to_hls(start_color)
        end_hls = color_to_hls(end_color)
        # use a list comprehension to build a list of interpolated hls values
        hls_values = [transition3(i, steps, start_hls, end_hls) for i in range(0, steps)]
        rgb_values = map(hls_to_color, hls_values)

    if colorspace == 'rgb':
        start_rgb = color_to_rgb(start_color)
        end_rgb = color_to_rgb(end_color)
        rgb_values = [transition3(i, steps, start_rgb, end_rgb) for i in range(0, steps)]
        rgb_values = map(rgb_to_color, rgb_values)

    print rgb_values
    # map back to rgb values
    return rgb_values

def lerp(value, maximum, start_point, end_point):
    """linear interpolation"""
    return start_point + (end_point - start_point)*value/maximum

def transition3(value, maximum, (s1, s2, s3), (e1, e2, e3)):
    r1= lerp(value, maximum, s1, e1)
    r2= lerp(value, maximum, s2, e2)
    r3= lerp(value, maximum, s3, e3)
    return (r1, r2, r3)

def pairwise(iterable):
    "s -> (s0,s1), (s2,s3), (s4, s5), ..."
    a = iter(iterable)
    return izip(a, a)
