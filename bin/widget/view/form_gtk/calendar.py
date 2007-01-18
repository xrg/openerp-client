##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
import datetime as DT
import gtk
from gtk import glade

import common
import interface
import locale

DT_FORMAT = '%Y-%m-%d'
DHM_FORMAT = '%Y-%m-%d %H:%M:%S'
HM_FORMAT = '%H:%M:%S'

if not hasattr(locale, 'nl_langinfo'):
	locale.nl_langinfo = lambda *a: '%x'

class calendar(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		interface.widget_interface.__init__(self, window, parent, attrs=attrs)
		self.win_gl = glade.XML(common.terp_path("terp.glade"),"widget_calendar")
		self.win_gl.signal_connect('on_but_calendar_clicked', self.cal_open)
		self.widget = self.win_gl.get_widget('widget_calendar')
		self.entry = self.win_gl.get_widget('ent_calendar')
		self.entry.connect('button_press_event', self._menu_open)
		self.state_set('valid')
		self.entry.connect('focus-in-event', lambda x,y: self._focus_in())
		self.entry.connect('focus-out-event', lambda x,y: self._focus_out())
		self.readonly=False

	def _color_widget(self):
		return self.entry

	def _readonly_set(self, value):
		interface.widget_interface._readonly_set(self, value)
		self.entry.set_editable(not value)
		self.entry.set_sensitive(not value)

	def get_value(self):
		str = self.entry.get_text()
		if str=='':
			return False
		try:
			date = time.strptime(str, locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y'))
		except:
			return False
		return time.strftime(DT_FORMAT, date)

	def set_value(self, model_field):
		model_field.set_client(self.get_value())
		return True

	def display(self, model_field):
		if not model_field:
			self.entry.set_text('')
			return False
		super(calendar, self).display(model_field)
		value = model_field.get()
		if not value:
			self.entry.set_text('')
		else:
			if len(value)>10:
				value=value[:10]
			date = time.strptime(value, DT_FORMAT)
			self.entry.set_text(time.strftime(locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y'), date))
		return True

	def cal_open(self, widget=None, val=None):
		if self.readonly:
			common.message(_('This widget is readonly !'))
			return True
		win_gl = glade.XML(common.terp_path("terp.glade"),"dia_form_wid_calendar")
		win = win_gl.get_widget('dia_form_wid_calendar')
		cal = win_gl.get_widget('cal_calendar')
		win.set_destroy_with_parent(True)
		try:
			val = self.get_value()
			if val:
				cal.select_month(int(val[5:7])-1, int(val[0:4]))
				cal.select_day(int(val[8:10]))
		except ValueError:
			pass
		response = win.run()
		if response == gtk.RESPONSE_OK:
			year, month, day = cal.get_date()
			dt = DT.date(year, month+1, day)
			self.entry.set_text(dt.strftime(locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y')))
		self._focus_out()
		win.destroy()

#
# To Bugfix
#

class datetime(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		interface.widget_interface.__init__(self, window, parent, model, attrs=attrs)
		self.win_gl = glade.XML(common.terp_path("terp.glade"),"widget_calendar")
		self.win_gl.signal_connect('on_but_calendar_clicked', self.cal_open)
		self.widget = self.win_gl.get_widget('widget_calendar')
		self.entry = self.win_gl.get_widget('ent_calendar')
		self.entry.connect('button_press_event', self._menu_open)
		self.state_set('valid')
		self.entry.connect('focus-in-event', lambda x,y: self._focus_in())
		self.entry.connect('focus-out-event', lambda x,y: self._focus_out())
		self.readonly=False
		self.value = ''

	def _color_widget(self):
		return self.entry

	def _readonly_set(self, value):
		self.readonly = value
		self.entry.set_editable(not value)
		self.entry.set_sensitive(not value)

	def get_value(self):
		str = self.entry.get_text()
		if str=='':
			return False
		try:
			date = time.strptime(str, locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y')+' %H:%M:%S')
		except:
			return False
		return time.strftime(DHM_FORMAT, date)

	def set_value(self, model_field):
		model_field.set_client(self.get_value())
		return True

	def display(self, model_field):
		if not model_field:
			return self.show(False)
		super(datetime, self).display(model_field)
		self.value = model_field.get()
		self.show(self.value)
	
	def show(self, dt_val):
		if not dt_val:
			self.entry.set_text('')
		else:
			date = time.strptime(dt_val, DHM_FORMAT)
			self.entry.set_text(time.strftime(locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y')+' %H:%M:%S', date))
		return True

	def cal_open(self, widget=None, val=None):
		if self.readonly:
			common.message(_('This widget is readonly !'))
			return True
		win_gl = glade.XML(common.terp_path("terp.glade"),"dia_form_wid_datetime")
		win = win_gl.get_widget('dia_form_wid_datetime')
		hour = win_gl.get_widget('hour')
		minute = win_gl.get_widget('minute')
		cal = win_gl.get_widget('calendar')
		win.set_destroy_with_parent(True)
		try:
			val = self.get_value()
			if val:
				hour.set_value(int(val[11:13]))
				minute.set_value(int(val[-5:-3]))
				cal.select_month(int(val[5:7])-1, int(val[0:4]))
				cal.select_day(int(val[8:10]))
			else:
				hour.set_value(time.localtime()[3])
				minute.set_value(time.localtime()[4])
		except ValueError:
			pass
		response = win.run()
		if response == gtk.RESPONSE_OK:
			hr = int(hour.get_value())
			mi = int(minute.get_value())
			dt = cal.get_date()
			month = str(dt[1]+1)
			if len(month)<2:
				month='0'+month
			day = str(dt[2])
			if len(day)<2:
				day='0'+day
			self.value = '%s-%s-%s %s:%s:00' % (str(dt[0]), month, day, hr, mi)
			self.show(self.value)
		self._focus_out()
		win.destroy()


class stime(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		interface.widget_interface.__init__(self, parent, attrs=attrs)
		self.win_gl = glade.XML(common.terp_path("terp.glade"),"widget_time")
		self.widget = self.win_gl.get_widget('widget_time')
		self.entry = self.win_gl.get_widget('widget_time_entry')
		self.value=False

	def _readonly_set(self, value):
		self.readonly = value
		self.entry.set_editable(not value)
		self.entry.set_sensitive(not value)

	def _color_widget(self):
		return self.entry

	def get_value(self):
		str = self.entry.get_text()
		if str=='':
			res = False 
		try: 
			t = time.strptime(str, '%H:%M:%S')
		except:
			res = False
		return time.strftime(HM_FORMAT, t)
		
	def set_value(self, model_field):
		res = self.get_value()
		model_field.set_client(res)
		return True

	def display(self, model_field):
		if not model_field:
			return self.show(False)
		super(stime, self).display(model_field)
		self.entry.set_text(model_field.get() or '00:00:00')
		return True

