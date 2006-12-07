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

import common
import wid_int

class spinbutton(wid_int.wid_int):
	def __init__(self, name, parent, attrs={}):
		wid_int.wid_int.__init__(self, name, parent, attrs)

		adj1 = gtk.Adjustment(0.0, -1000000000.0, 1000000000, 1.0, 5.0, 5.0)
		adj2 = gtk.Adjustment(0.0, -1000000000.0, 1000000000, 1.0, 5.0, 5.0)
		self.win_gl = glade.XML(common.terp_path("terp.glade"),"wid_sea_int")
		self.widget = self.win_gl.get_widget('wid_sea_int')

		self.spin1 = self.win_gl.get_widget('sea_spin1')
		self.spin2 = self.win_gl.get_widget('sea_spin2')
		self.spin1.configure(adj1, 0.01, int( attrs.get('digits',(14,2))[1] ))
		self.spin2.configure(adj2, 0.01, int( attrs.get('digits',(14,2))[1] ))
		self.spin1.set_text('')
		self.spin2.set_text('')
		self.spin1.set_activates_default(True)
		self.spin2.set_activates_default(True)

	def _value_get(self):
		res = []
		if float(self.spin1.get_text())>0 and float(self.spin2.get_text())==0.0:
			res.append((self.name, '=', float(self.spin1.get_text())))
		elif float(self.spin1.get_text())>0:
			res.append((self.name, '>=', float(self.spin1.get_text())))
		if float(self.spin2.get_text())>0:
			res.append((self.name, '<=', float(self.spin2.get_text())))
		return res

	def _value_set(self, value):
		self.spin1.set_text(str(value))
		self.spin2.set_text(str(value))

	value = property(_value_get, _value_set, None,
	  'The content of the widget or ValueError if not valid')

	def clear(self):
		self.value = False
