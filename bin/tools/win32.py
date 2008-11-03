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
import time
import datetime 
import locale

if not hasattr(locale, 'nl_langinfo'):
    def nl_langinfo(param):
        val = time.strptime('30/12/2004', '%d/%m/%Y')
        dt = datetime.datetime(*val[:-2])
        format_date = dt.strftime('%x')
        for x, y in [('30','%d'),('12','%m'),('2004','%Y'),('04','%Y')]:
            format_date = format_date.replace(x,y)
        return format_date
    locale.nl_langinfo = nl_langinfo


    if not hasattr(locale, 'D_FMT'):
        locale.D_FMT = None

