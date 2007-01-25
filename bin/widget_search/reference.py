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
import rpc

class reference(wid_int.wid_int):
	def __init__(self, name, parent, attrs={}):
		wid_int.wid_int.__init__(self, name, parent, attrs)
		self.win_gl = glade.XML(common.terp_path("terp.glade"),"widget_reference", gettext.textdomain())
		self.win_gl.signal_connect('on_but_clear_clicked', self.clear)
		self.widget = self.win_gl.get_widget('widget_reference')

		self.model = attrs['args']

		self.wid_id = self.win_gl.get_widget('ent_id')
		self.wid_text = self.win_gl.get_widget('ent_reference')
		self.wid_text.connect('activate', self.sig_activate)
		self.wid_text.connect('changed', self.sig_changed)
		self._value=None

	def sig_activate(self, *args):
		self.wid_id.set_text(str(self._value[0]))

	def sig_changed(self, *args):
		self.wid_id.set_text('-')
	
	def _value_get(self):
		if self._value:
			return self._value[0]
		else:
			return False

	def _value_set(self, value):
		self._value = value
		if self.value!=False:
			self.wid_text.set_text( value[1] )
			self.wid_id.set_text( str(value[0]) )
		else:
			self.wid_text.set_text( '' )
			self.wid_id.set_text( '' )

	value = property(_value_get, _value_set, None,
	  'The content of the widget or ValueError if not valid')

	def clear(self, widget=None):
		self.value = False
