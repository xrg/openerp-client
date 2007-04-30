##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: parser.py 4698 2006-11-27 12:30:44Z ced $
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


import locale
import gtk
from gtk import glade

import tools
import rpc
from widget.view import interface

from pychart import *

import StringIO

import datetime as DT
import time

DT_FORMAT = '%Y-%m-%d'
DHM_FORMAT = '%Y-%m-%d %H:%M:%S'
HM_FORMAT = '%H:%M:%S'

if not hasattr(locale, 'nl_langinfo'):
	locale.nl_langinfo = lambda *a: '%x'

if not hasattr(locale, 'D_FMT'):
	locale.D_FMT = None


theme.use_color = 1

class ViewGraph(object):
	def __init__(self, widget, model, axis, fields, axis_data={}, attrs={}):
		self.widget = widget
		self.fields = fields
		self.model = model
		self.axis = axis
		self.editable = False
		self.widget.editable = False
		self.axis_data = axis_data
		self.attrs = attrs

	def display(self, models):
		import os
		datas = []
		theme.reinitialize()
		for m in models:
			res = {}
			for x in self.axis:
				if self.fields[x]['type'] in ('many2one', 'char','time','text','selection'):
					res[x] = str(m[x].get_client(m))
				elif self.fields[x]['type'] == 'date':
					date = time.strptime(m[x].get_client(m), DT_FORMAT)
					res[x] = time.strftime(locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y'), date)
				elif self.fields[x]['type'] == 'datetime':
					date = time.strptime(m[x].get_client(m), DHM_FORMAT)
					if 'tz' in rpc.session.context:
						try:
							import pytz
							lzone = pytz.timezone(rpc.session.context['tz'])
							szone = pytz.timezone(rpc.session.timezone)
							dt = DT.datetime(date[0], date[1], date[2], date[3], date[4], date[5], date[6])
							sdt = szone.localize(dt, is_dst=True)
							ldt = sdt.astimezone(lzone)
							date = ldt.timetuple()
						except:
							pass
					res[x] = time.strftime(locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y')+' %H:%M:%S', date)
				else:
					res[x] = float(m[x].get_client(m))
			datas.append(res)


		operators = {
			'+': lambda x,y: x+y,
			'*': lambda x,y: x*y,
			'min': lambda x,y: min(x,y),
			'max': lambda x,y: max(x,y),
			'**': lambda x,y: x**y
		}
		for field in self.axis_data:
			group = self.axis_data[field].get('group', False)
			if group:
				keys = {}
				for d in datas:
					if d[field] in keys:
						for a in self.axis:
							if a<>field:
								oper = operators[self.axis_data[a].get('operator', '+')]
								keys[d[field]][a] = oper(keys[d[field]][a], d[a])
					else:
						keys[d[field]] = d
				datas = keys.values()

		data = []
		for d in datas:
			res = []
			for x in self.axis:
				if hasattr(d[x], 'replace'):
					res.append(d[x].replace('/', '//'))
				else:
					res.append(d[x])
			data.append(res)

		if not data:
			self.widget.set_from_stock('gtk-no', gtk.ICON_SIZE_BUTTON)
			return False

#		try:
		png_string = StringIO.StringIO()
		can = canvas.init(fname=png_string, format='png')

		area_args = {
			'size': (200,150)
		}
		if self.attrs.get('type','pie')=='pie':
			ar = area.T(
				x_grid_style= None,
				y_grid_style= None,
				legend= legend.T(),
				**area_args
			)
			plot = pie_plot.T(
				data=data,
				arc_offsets=[0,10,0,10],
				shadow = (2, -2, fill_style.gray50),
				label_offset = 25,
				arrow_style = arrow.a3
			)
			ar.add_plot(plot)
		elif self.attrs['type']=='bar':
			valmin = valmax = 0
			for i in range(1,len(self.axis)):
				for d in data:
					valmin = min(valmin,d[i])
					valmax = max(valmax,d[i])
			ar = area.T(
				x_coord = category_coord.T(data, 0),
				x_axis = axis.X(label=self.fields[self.axis[0]]['string'].replace('/','//'), format="/a90 %s"),
				y_axis = axis.Y(label=None, minor_tic_interval=(valmax - valmin)/10),
				y_range = (valmin, valmax),
				y_grid_interval = (valmax - valmin)/10,
				**area_args
			)
			for i in range(1,len(self.axis)):
				plot = bar_plot.T(
					data=data,
					label = self.fields[self.axis[i]]['string'],
					cluster = (i-1, len(self.axis)-1),
					hcol = i
				)
				ar.add_plot(plot)
		else:
			raise 'Graph type '+self.attrs['type']+' does not exist !'

		ar.draw(can)
		can.close()

		data = png_string.getvalue()
		loader = gtk.gdk.PixbufLoader ('png')

		loader.write (data, len(data))
		pixbuf = loader.get_pixbuf()
		loader.close()
		npixbuf = pixbuf.add_alpha(True, chr(0xff), chr(0xff), chr(0xff))
		self.widget.set_from_pixbuf(npixbuf)
#		except Exception,e:
#			print e
#			self.widget.set_from_stock('gtk-no', gtk.ICON_SIZE_BUTTON)
#			return False

