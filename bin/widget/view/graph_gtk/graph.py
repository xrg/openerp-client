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

import tinygraph

import matplotlib

matplotlib.rcParams['xtick.labelsize'] = 10
matplotlib.rcParams['ytick.labelsize'] = 10

from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo as FigureCanvas


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


class ViewGraph(object):
	def __init__(self, model, axis, fields, axis_data={}, attrs={}):
		self.widget = gtk.HBox()
		self._figure = Figure(figsize=(800,600), dpi=100, facecolor='w')
		self._subplot = self._figure.add_subplot(111,axisbg='#eeeeee')
		self._canvas = FigureCanvas(self._figure)
		self.widget.pack_start(self._canvas, expand=True, fill=True)

		if attrs.get('type', 'pie')=='bar':
			if attrs.get('orientation', 'vertical')=='vertical':
				self._figure.subplots_adjust(left=0.08,right=0.98,bottom=0.25,top=0.98)
			else:
				self._figure.subplots_adjust(left=0.20,right=0.97,bottom=0.07,top=0.98)
		else:
			self._figure.subplots_adjust(left=0.03,right=0.97,bottom=0.03,top=0.97)

		self.fields = fields
		self.model = model
		self.axis = axis
		self.editable = False
		self.widget.editable = False
		self.axis_data = axis_data
		self.axis_group = {}
		for i in self.axis_data:
			self.axis_data[i]['string'] = self.fields[i]['string']
			if self.axis_data[i].get('group', False):
				self.axis_group[i]=1
				self.axis.remove(i)
		self.attrs = attrs

	def display(self, models):
		datas = []
		for m in models:
			res = {}
			for x in self.axis_data.keys():
				if self.fields[x]['type'] in ('many2one', 'char','time','text'):
					res[x] = str(m[x].get_client(m))
				elif self.fields[x]['type'] == 'selection':
					selection = dict(m[x].attrs['selection'])
					val = str(m[x].get_client(m))
					res[x] = selection.get(val, val)
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
		tinygraph.tinygraph(self._subplot, self.attrs.get('type', 'pie'), self.axis, self.axis_data, datas, axis_group_field=self.axis_group, orientation=self.attrs.get('orientation', 'vertical'))
		# the draw function may generate exception but it is not a problem as it will be redraw latter
		try:
			self._subplot.draw()
			#XXX it must have some better way to force the redraw but this one works
			self._canvas.queue_resize()
		except:
			pass
