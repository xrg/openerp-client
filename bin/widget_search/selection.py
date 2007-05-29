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

class selection(wid_int.wid_int):
	def __init__(self, name, parent, attrs={}):
		wid_int.wid_int.__init__(self, name, parent, attrs)

		self.widget = gtk.combo_box_entry_new_text()
		self.widget.child.set_editable(False)
		self._selection={}
		if 'selection' in attrs:
			self.set_popdown(attrs.get('selection',[]))

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
		model = self.widget.get_model()
		index = self.widget.get_active()
		if index>=0:
			res = self._selection.get(model[index][0], False)
			if res:
				return [(self.name,'=',res)]
		return []

	def _value_set(self, value):
		if value==False:
			value=''
		for s in self._selection:
			if self._selection[s]==value:
				self.widget.child.set_text(s)

	def clear(self):
		self.value = ''

	value = property(_value_get, _value_set, None,
	  'The content of the widget or ValueError if not valid')

	def _readonly_set(self, value):
		self.widget.set_sensitive(not value)
