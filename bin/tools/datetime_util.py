# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from mx.DateTime import RelativeDateTime
from mx.DateTime import now

try:
    from mx.DateTime import strptime
except ImportError:
    # strptime does not exist on windows. we emulate it
    from mx.DateTime import mktime
    def strptime(s, f):
        return mktime(time.strptime(s, f))

date_operation = {
    '^=w(\d+)$': lambda dt,r: dt+RelativeDateTime(day=0, month=0, weeks = int(r.group(1))),
    '^=d(\d+)$': lambda dt,r: dt+RelativeDateTime(day=int(r.group(1))),
    '^=m(\d+)$': lambda dt,r: dt+RelativeDateTime(month = int(r.group(1))),
    '^=y(2\d\d\d)$': lambda dt,r: dt+RelativeDateTime(year = int(r.group(1))),
    '^=h(\d+)$': lambda dt,r: dt+RelativeDateTime(hour = int(r.group(1))),
    '^=(\d+)w$': lambda dt,r: dt+RelativeDateTime(day=0, month=0, weeks = int(r.group(1))),
    '^=(\d+)d$': lambda dt,r: dt+RelativeDateTime(day=int(r.group(1))),
    '^=(\d+)m$': lambda dt,r: dt+RelativeDateTime(month = int(r.group(1))),
    '^=(2\d\d\d)y$': lambda dt,r: dt+RelativeDateTime(year = int(r.group(1))),
    '^=(\d+)h$': lambda dt,r: dt+RelativeDateTime(hour = int(r.group(1))),
    '^([\\+-]\d+)h$': lambda dt,r: dt+RelativeDateTime(hours = int(r.group(1))),
    '^([\\+-]\d+)w$': lambda dt,r: dt+RelativeDateTime(days = 7*int(r.group(1))),
    '^([\\+-]\d+)d$': lambda dt,r: dt+RelativeDateTime(days = int(r.group(1))),
    '^([\\+-]\d+)m$': lambda dt,r: dt+RelativeDateTime(months = int(r.group(1))),
    '^([\\+-]\d+)y$': lambda dt,r: dt+RelativeDateTime(years = int(r.group(1))),
    '^=$': lambda dt,r: now(),
    '^-$': lambda dt,r: False
}

date_mapping = {
    '%y': ('__', '[_0-9][_0-9]'),
    '%Y': ('____', '[_1-9][_0-9][_0-9][_0-9]'),
    '%m': ('__', '[_0-1][_0-9]'),
    '%d': ('__', '[_0-3][_0-9]'),
    '%H': ('__', '[_0-2][_0-9]'),
    '%M': ('__', '[_0-6][_0-9]'),
    '%S': ('__', '[_0-6][_0-9]'),
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

