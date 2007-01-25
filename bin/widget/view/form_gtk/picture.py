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

import gtk
from gtk import glade
import gettext

import interface
import os

import common

class wid_picture(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		interface.widget_interface.__init__(self, window, parent, model, attrs)
		self.win_gl = glade.XML(common.terp_path("terp.glade"),"widget_picture", gettext.textdomain())
		self.widget = self.win_gl.get_widget('widget_picture')

		self.wid_picture = self.win_gl.get_widget('widget_picture_view')
		self.value=False

	def value_set(self, model_field):
		self.model_field.set( self._value )

	def display(self, model_field):
		if not model_field:
			return False
		super(wid_picture, self).display(model_field)
		value = model_field.get()
		import base64
		self._value = value
		if self._value:
			value = base64.decodestring(self._value)
			loader = gtk.gdk.PixbufLoader('jpeg')
			loader.write (value, len(value))
			pixbuf = loader.get_pixbuf()
			loader.close()
			self.wid_picture.set_from_pixbuf(pixbuf)
		else:
			self.wid_picture.set_from_pixbuf(None)
