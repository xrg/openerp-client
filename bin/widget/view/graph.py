##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: list.py 4411 2006-11-02 23:59:17Z pinky $
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

import gobject
import gtk

class ViewGraph(object):

	def __init__(self, screen, widget, children={}, buttons={}, toolbar=None):
		self.screen = screen
		self.view_type = 'graph'
		#self.model_add_new = True
		self.widget = widget
		self.image = widget
		self.widget.screen = screen

	def cancel(self):
		pass

	def __str__(self):
		return 'ViewGraph (%s)' % self.screen.resource

	def __getitem__(self, name):
		return None

	def destroy(self):
		self.widget.destroy()
		del self.screen
		del self.widget

	def set_value(self):
		pass

	def reset(self):
		pass

	#
	# self.widget.set_model(self.store) could be removed if the store
	# has not changed -> better ergonomy. To test
	#
	def display(self):
		if self.screen.models:
			print self.screen.models
			self.image.set_from_stock('gtk-close', gtk.ICON_SIZE_BUTTON)
		print 'DISPLAY'

		from pychart import *
		import os

		data = [("foo", 10),("bar", 20), ("baz", 30), ("ao", 40)]

		png_string = file(os.tempnam(), 'w')
		can = canvas.init(fname=png_string, format='png')

		ar = area.T(
			size=(150,150),
			legend=legend.T(),
			x_grid_style = None,
			y_grid_style = None
		)

		plot = pie_plot.T(
			data=data,
			arc_offsets=[0,10,0,10],
			shadow = (2, -2, fill_style.gray50),
			label_offset = 25,
			arrow_style = arrow.a3
		)
		ar.add_plot(plot)
		ar.draw(can)
		can.close()

		png_string.flush()

		pixbuf = gtk.gdk.pixbuf_new_from_file(png_string.name)
		self.image.set_from_pixbuf(pixbuf)
		return None

	def signal_record_changed(self, *args):
		pass

	def sel_ids_get(self):
		return []

	def on_change(self, callback):
		pass

	def unset_editable(self):
		pass

