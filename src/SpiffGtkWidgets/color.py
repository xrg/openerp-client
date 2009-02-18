# Copyright (C) 2008 Samuel Abels, http://debain.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import gtk.gdk

########################
# Explicit converters.
########################
def str2gdk(name):
    return gtk.gdk.color_parse(name)

def int2gdk(i):
    red   = (i >> 24) & 0xff
    green = (i >> 16) & 0xff
    blue  = (i >>  8) & 0xff
    return gtk.gdk.Color(red * 256, green * 256, blue * 256)

def rgb2gdk(color):
    red   = int(color[0] * 65535)
    green = int(color[1] * 65535)
    blue  = int(color[2] * 65535)
    return gtk.gdk.Color(red, green, blue)

def rgba2gdk(color):
    red   = int(color[0] * 65535)
    green = int(color[1] * 65535)
    blue  = int(color[2] * 65535)
    value = int(color[3] * 65535) # not supported by gdk.Color
    return gtk.gdk.Color(red, green, blue)

def gdk2int(color):
    return (color.red   / 256 << 24) \
         | (color.green / 256 << 16) \
         | (color.blue  / 256 <<  8) \
         | 0xff

def gdk2rgb(color):
    return (color.red / 65535.0, color.green / 65535.0, color.blue / 65535.0)

def gdk2rgba(color):
    return (color.red / 65535.0, color.green / 65535.0, color.blue / 65535.0, 1)

########################
# Automatic converters.
########################
def to_gdk(color):
    if isinstance(color, gtk.gdk.Color):
        return color
    elif type(color) == type(0) or type(color) == type(0l):
        return int2gdk(color)
    elif type(color) == type(''):
        return str2gdk(color)
    elif type(color) == type(()) and len(color) == 3:
        return rgb2gdk(color)
    elif type(color) == type(()) and len(color) == 4:
        return rgba2gdk(color)
    else:
        raise TypeError('%s is not a known color type' % type(color))

def to_int(color):
    return gdk2int(to_gdk(color))

def to_rgb(color):
    return gdk2rgb(to_gdk(color))

def to_rgba(color):
    return gdk2rgba(to_gdk(color))

########################
# Other functions.
########################
palette = [(0.12,       0.29,       0.49),
           (0.36,       0.51,       0.71),
           (0.75,       0.31,       0.30),
           (0.62,       0.73,       0.38),
           (0.50,       0.40,       0.63),
           (0.29,       0.67,       0.78),
           (0.96,       0.62,       0.34),
           (1.0 - 0.12, 1.0 - 0.29, 1.0 - 0.49),
           (1.0 - 0.36, 1.0 - 0.51, 1.0 - 0.71),
           (1.0 - 0.75, 1.0 - 0.31, 1.0 - 0.30),
           (1.0 - 0.62, 1.0 - 0.73, 1.0 - 0.38),
           (1.0 - 0.50, 1.0 - 0.40, 1.0 - 0.63),
           (1.0 - 0.29, 1.0 - 0.67, 1.0 - 0.78),
           (1.0 - 0.96, 1.0 - 0.62, 1.0 - 0.34)]
def from_string(string, n_colors = 1):
    first = string.__hash__() % len(palette)
    if n_colors == 1:
        return palette[first]
    return [palette[i] for i in range(first, first + n_colors)]
