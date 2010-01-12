# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

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
# Tango colors:
# http://tango.freedesktop.org/Tango_Icon_Theme_Guidelines
#           light       mid       dark
palette = (('#fce94f', '#edd400', '#c4a000'),  # Butter
           ('#fcaf3e', '#f57900', '#ce5c00'),  # Orange
           ('#e9b96e', '#c17d11', '#8f5902'),  # Chocolate
           ('#8ae234', '#73d216', '#4e9a06'),  # Chameleon
           ('#729fcf', '#3465a4', '#204a87'),  # Sky Blue
           ('#ad7fa8', '#75507b', '#5c35cc'),  # Plum
           ('#ef2929', '#cc0000', '#a40000'),  # Scarlet Red
           ('#eeeeec', '#d3d7cf', '#babdb6'),  # Aluminium (bright)
           ('#888a85', '#555753', '#2e3436'))  # Aluminium (dark)
def from_string(string, n_colors = 1):
    string += 'b'
    tuple = palette[string.__hash__() % len(palette)]
    if n_colors == 1:
        return to_rgb(tuple[0])
    return [to_rgb(color) for color in tuple[:n_colors]]

def bg_color2text_color(color):
    if sum(to_rgb(color)) > 1.9:
        return 0, 0, 0
    return 1, 1, 1
