import gtk.gdk

def str2gdk(name):
    return gtk.gdk.color_parse(name)

def int2gdk(i):
    red   = (i >> 24) & 0xff
    green = (i >> 16) & 0xff
    blue  = (i >>  8) & 0xff
    return gtk.gdk.Color(red * 256, green * 256, blue * 256)

def gdk2int(color):
    return (color.red   / 256 << 24) \
         | (color.green / 256 << 16) \
         | (color.blue  / 256 <<  8) \
         | 0xff

def gdk2rgb(color):
    return (color.red / 65535.0, color.green / 65535.0, color.blue / 65535.0)

def gdk2rgba(color):
    return (color.red / 65535.0, color.green / 65535.0, color.blue / 65535.0, 1)

def convert(color, converter):
    if isinstance(color, gtk.gdk.Color):
        pass
    elif type(color) == type(0) or type(color) == type(0l):
        color = int2gdk(color)
    elif type(color) == type(''):
        color = str2gdk(color)
    else:
        raise TypeError('%s is not a known color type' % type(color))
    return converter(color)

def to_int(color):
    return convert(color, gdk2int)

def to_rgb(color):
    return convert(color, gdk2rgb)

def to_rgba(color):
    return convert(color, gdk2rgba)
