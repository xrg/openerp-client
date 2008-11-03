# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

def logged(showtime):
    def log(f, res, *args, **kwargs):
        vector = ['Call -> function: %s' % f]
        for i, arg in enumerate(args):
            vector.append( '  arg %02d: %r' % ( i, arg ) )
        for key, value in kwargs.items():
            vector.append( '  kwarg %10s: %r' % ( key, value ) )
        vector.append( '  result: %r' % res )
        print "\n".join(vector)

    def outerwrapper(f):
        def wrapper(*args, **kwargs):
            if showtime:
                import time
                now = time.time()
            res = None
            try:
                res = f(*args, **kwargs)
                return res
            finally:
                log(f, res, *args, **kwargs)
                if showtime:
                    print "  time delta: %s" % (time.time() - now)
        return wrapper
    return outerwrapper

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
