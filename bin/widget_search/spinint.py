##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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

import common
import wid_int

class spinint(wid_int.wid_int):
	def __init__(self, name, parent, attrs={}):
		wid_int.wid_int.__init__(self, name, attrs)

		self.widget = gtk.HBox(spacing=3)

		adj1 = gtk.Adjustment(0.0, 0.0, 1000000000, 1.0, 5.0, 5.0)
		self.spin1 = gtk.SpinButton(adj1, 1, digits=0)
		self.spin1.set_numeric(True)
		self.widget.pack_start(self.spin1, expand=False, fill=True)

		self.widget.pack_start(gtk.Label('-'), expand=False, fill=False)

		adj2 = gtk.Adjustment(0.0, 0.0, 1000000000, 1.0, 5.0, 5.0)
		self.spin2 = gtk.SpinButton(adj2, 1, digits=0)
		self.spin2.set_numeric(True)
		self.widget.pack_start(self.spin2, expand=False, fill=True)

	def _value_get(self):
		res = []
		self.spin1.update()
		self.spin2.update()
		if (self.spin1.get_value_as_int() > 0) and (self.spin2.get_value_as_int() == 0):
			res.append((self.name, '=', self.spin1.get_value_as_int()))
		elif self.spin1.get_value_as_int() > 0:
			res.append((self.name, '>=', self.spin1.get_value_as_int()))
		if self.spin2.get_value_as_int() > 0:
			res.append((self.name, '<=', self.spin2.get_value_as_int()))
		return res

	def _value_set(self, value):
		self.spin1.set_value(value)
		self.spin2.set_value(value)

	value = property(_value_get, _value_set, None, _('The content of the widget or ValueError if not valid'))

	def clear(self):
		self.value = 0.0
