##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
import gtk
import common
from gtk import glade
import gettext

import wid_int

DT_FORMAT = '%Y-%m-%d'

class calendar(wid_int.wid_int):
	def __init__(self, name, parent, attrs={}):
		wid_int.wid_int.__init__(self, name, parent, attrs)
		self.win_gl = glade.XML(common.terp_path("terp.glade"),"wid_sea_cal", gettext.textdomain())

		self.widget = self.win_gl.get_widget('wid_sea_cal')
		self.entry1 = self.win_gl.get_widget('sea_ent1')
		self.entry2 = self.win_gl.get_widget('sea_ent2')
		self.win_gl.signal_connect('on_cal1_event', self.cal_open, self.entry1)
		self.win_gl.signal_connect('on_cal2_event', self.cal_open, self.entry2)

	# converts from locale specific format to our internal format
	def _date_get(self, str):
		try:
			date = time.strptime(str, '%x')
		except:
			return False
		return time.strftime(DT_FORMAT, date)

	def _value_get(self):
		res = []
		val = self.entry1.get_text()
		if val:
			res.append((self.name, '>=', self._date_get(val)))
		val = self.entry2.get_text()
		if val:
			res.append((self.name, '<=', self._date_get(val)))
		return res

	def _value_set(self, value):
		pass

	value = property(_value_get, _value_set, None,
	  'The content of the widget or ValueError if not valid')

	# dest = the first or the second entry (dates are inputed in range of dates)
	def cal_open(self, widget, event, dest):
		win_gl = glade.XML(common.terp_path("terp.glade"),"dia_form_wid_calendar", gettext.textdomain())
		win = win_gl.get_widget('dia_form_wid_calendar')
		cal = win_gl.get_widget('cal_calendar')
		try:
			val = self._date_get(dest.get_text())
			if val:
				cal.select_month(int(val[5:7])-1, int(val[0:4]))
				cal.select_day(int(val[8:10]))
		except ValueError:
			pass
		response = win.run()
		if response == gtk.RESPONSE_OK:
			dt = cal.get_date()
			month = str(dt[1]+1)
			if len(month)<2:
				month='0'+month
			day = str(dt[2])
			if len(day)<2:
				day='0'+day
			value = str(dt[0])+'-'+month+'-'+day
			date = time.strptime(value, DT_FORMAT)
			dest.set_text(time.strftime('%x', date))
		win.destroy()

	def clear(self):
		self.value = ''

