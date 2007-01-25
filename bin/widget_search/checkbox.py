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

class checkbox(wid_int.wid_int):
	def __init__(self, name, parent, attrs={}):
		wid_int.wid_int.__init__(self, name, attrs)
		self.win_gl = glade.XML(common.terp_path("terp.glade"),"wid_sea_check2", gettext.textdomain())
		self.widget = self.win_gl.get_widget('wid_sea_check2')

		self.entry = self.win_gl.get_widget('combobox_checkbox').child
		self.entry.set_editable(False)

	def _value_get(self):
		val = self.entry.get_text()
		if val:
			return [(self.name,'=',int(val=='Yes'))]
		return []

	def _value_set(self, value):
		pass

	value = property(_value_get, _value_set, None,
	  'The content of the widget or ValueError if not valid')
