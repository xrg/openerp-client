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
import wid_int
import rpc

#CHECKME: ca devrait pas etre one2many?????????????????????
class many2one(wid_int.wid_int):
	def __init__(self, name,parent, attrs={}):
		wid_int.wid_int.__init__(self, name, parent, attrs)
		self.widget = gtk.Entry(int(attrs.get('length',0)))
		self.widget.set_width_chars(5)
		self.model_type = attrs['relation']
		self.widget.connect('changed', self.sig_changed)
		self._cache = False

	def _value_get(self):
		s = self.widget.get_text()
		if s:
			return [(self.name,self.attrs.get('comparator','ilike'),s)]
		else:
			return []

	def _value_set(self, value):
		if value:
			self.widget.set_text(value)

	def clear(self):
		self.value = ''

	value = property(_value_get, _value_set, None,
	  'The content of the widget or ValueError if not valid')

