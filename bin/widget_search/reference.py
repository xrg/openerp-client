##############################################################################
#
# Copyright (c) 2004-2008 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import common
import wid_int
import rpc

class reference(wid_int.wid_int):
	def __init__(self, name, parent, attrs={}):
		wid_int.wid_int.__init__(self, name, parent, attrs)

		self.widget = gtk.combo_box_entry_new_text()
		self.widget.child.set_editable(False)

		self.set_popdown(attrs.get('selection', []))

	def get_model(self):
		res = self.widget.child.get_text()
		return self._selection.get(res, False)

	def set_popdown(self, selection):
		model = self.widget.get_model()
		model.clear()
		self._selection={}
		lst = []
		for (i,j) in selection:
			name = str(j)
			if type(i)==type(1):
				name+=' ('+str(i)+')'
			lst.append(name)
			self._selection[name]=i
		self.widget.append_text('')
		for l in lst:
			self.widget.append_text(l)
		return lst

	def _value_get(self):
		if self.get_model():
			return [(self.name, 'like', self.get_model()+',')]
		else:
			return []

	def _value_set(self, value):
		if value==False:
			value=''
		for s in self._selection:
			if self._selection[s]==value:
				self.widget.child.set_text(s)


	value = property(_value_get, _value_set, None, _('The content of the widget or ValueError if not valid'))

	def clear(self, widget=None):
		self.value = ''
