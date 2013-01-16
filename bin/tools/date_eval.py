# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2010-2011 OpenERP (http://www.openerp.com)
#    Author: P. Christeas <xrg@openerp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import re
# import time
import datetime
from dateutil.relativedelta import relativedelta

re_abstimes = { 'now': datetime.datetime.now,
                'today': datetime.date.today,
                'tomorrow': lambda: (datetime.date.today() + datetime.timedelta(1)),
                'yesterday': lambda: (datetime.date.today() - datetime.timedelta(1)),
                }

rel_units = { 'yr' : 'Y',
            'year': 'Y',
            'years': 'Y',
            'month': 'M',
            'months': 'M',
            'mo': 'M',
            'd': 'D',
            'day': 'D',
            'days': 'D',
            'h': 3600,
            'hr': 3600,
            'hour': 3600,
            'hours': 3600,
            'm': 60,
            'min': 60,
            'minute': 60,
            'minutes': 60,
            's': 1,
            'sec' : 1,
            'second': 1,
            'seconds': 1,
            }

re_dateeval = re.compile(r"(?P<abs>" + '|'.join(re_abstimes) +")"
        r"|(?:(?P<rel>(?:\+|-)[0-9]+)(?P<rel_unit>" + '|'.join(rel_units)+ "))"
        r"|(?: ?\bon ?(?P<date>[0-9]{1,2}(?:/[0-9]{1,2}(?:/[0-9]{2,4})?)?))"
        r"|(?: ?\bat ?(?P<time>[0-9]{1,2}(?::[0-9]{2}(?::[0-9]{2})?)?))"
        r"| +", re.I)

def date_eval(rstr):
    """ Evaluate an textual representation of date/time into a datetime structure
    
        @param rstr the string representation
        @return a datetime.datetime object

        The representation is *strictly* in English.

        The parser is a loop that parses the expression left-to-right, manipulating
        the computed timestamp at each step. So the order of sub-expressions
        is important!


        Possible sub-expressions:
        
        * Absolute (current clock):
            - now : Current timestamp of the computer clock
            - today : Midnight at current date: 02/03/2011 00:00:00
            - tomorrow : Midnight at next date
            - yesterday : Midnight of previous date
        * Relative (to previous sub-expression): +/-Num<unit> where Num is a number
          and unit can be one of:
            - year(s)
            - month(s)
            - day(s)
            - h[our(s)]
            - m[inute(s)]
            - s[ec[ond(s)]]
        * Date/time : A partial or full date or time can be applied to specify
          date and/or time:
            - on DD[/MM[/YY]] : specify DD=day, MM=month or even YY=year
            - at HH[:mm[:ss]] : specify HH=hour, mm=minute or even ss=seconds

        Examples::

            now +3days -2min
            today at 13:45:00
            on 15-04 at 13:45
            today +1year at 12:30
    """
    cur_time = datetime.datetime.now()
    for m in re_dateeval.finditer(rstr):
        if m.group('abs'):
            cur_time = re_abstimes[m.group('abs')]()
            if not isinstance(cur_time, datetime.datetime):
                cur_time = datetime.datetime.fromordinal(cur_time.toordinal())
            
        elif m.group('rel'):
            mrel = int(m.group('rel')[1:])
            if m.group('rel')[0] == '-':
                mrel = 0 - mrel
            mun = rel_units[m.group('rel_unit')]
            if mun == 'Y':
                drel = relativedelta(years=mrel)
            elif mun == 'M':
                drel = relativedelta(months=mrel)
            elif mun == 'D':
                drel = datetime.timedelta(days=mrel)
            else:
                drel = mrel * datetime.timedelta(seconds=mun)

            cur_time = cur_time + drel
        elif m.group('date'):
            dli = map(int, m.group('date').split('/'))
            if len(dli) == 2:
                dli += [cur_time.year,]
            elif len(dli) == 1:
                dli += [cur_time.month, cur_time.year]
            cur_time = datetime.datetime.combine(datetime.date(dli[2],dli[1],dli[0]), cur_time.time())
        elif m.group('time'):
            dli = map(int, m.group('time').split(':'))
            if len(dli) == 2:
                dli += [cur_time.second,]
            elif len(dli) == 1:
                dli += [cur_time.minute, cur_time.second]
            cur_time = datetime.datetime.combine(cur_time.date(), datetime.time(dli[0],dli[1],dli[2]))
        else:
            pass

    return cur_time

#eof
