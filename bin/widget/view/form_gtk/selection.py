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

import common
import interface
import gtk
import gobject

import gettext


class selection(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		interface.widget_interface.__init__(self, window, parent, model, attrs)

		self.widget = gtk.HBox(spacing=3)
		self.entry = gtk.ComboBoxEntry()
		self.entry.child.set_property('activates_default', True)
		self.entry.child.connect('changed', self.sig_changed)
		self.entry.child.connect('button_press_event', self._menu_open)
		self.entry.child.connect('activate', self.sig_activate)
		self.entry.child.connect_after('focus-out-event', self.sig_activate)
		self.entry.set_size_request(int(attrs.get('size', -1)), -1)
		self.widget.pack_start(self.entry, expand=True, fill=True)

		self.ok = True
		self._selection={}
		self.set_popdown(attrs.get('selection',[]))
		self.last_key = (None, 0)

	def set_popdown(self, selection):
		model = gtk.ListStore(gobject.TYPE_STRING)
		self._selection={}
		lst = []
		for (value, name) in selection:
			name = str(name)
			lst.append(name)
			self._selection[name] = value
			i = model.append()
			model.set(i, 0, name)
		self.entry.set_model(model)
		self.entry.set_text_column(0)
		return lst

	def _readonly_set(self, value):
		interface.widget_interface._readonly_set(self, value)
		self.entry.set_sensitive(not value)

	def value_get(self):
		res = self.entry.child.get_text()
		return self._selection.get(res, False)

	def sig_activate(self, *args):
		text = self.entry.child.get_text()
		value = False
		if text:
			for txt, val in self._selection.items():
				if not val:
					continue
				if txt[:len(text)].lower() == text.lower():
					value = val
					if len(txt) == len(text):
						break
		self._view.modelfield.set_client(self._view.model, value, force_change=True)
		self.display(self._view.model, self._view.modelfield)


	def set_value(self, model, model_field):
		model_field.set_client(model, self.value_get())

	def _menu_sig_default_set(self):
		self.set_value(self._view.model, self._view.modelfield)
		super(selection, self)._menu_sig_default_set()

	def display(self, model, model_field):
		self.ok = False
		if not model_field:
			self.entry.child.set_text('')
			self.ok = True
			return False
		super(selection, self).display(model, model_field)
		value = model_field.get(model)
		if not value:
			self.entry.child.set_text('')
		else:
			found = False
			for long_text, sel_value in self._selection.items():
				if sel_value == value:
					self.entry.child.set_text(long_text)
					found = True
					break
		self.ok = True

	def sig_changed(self, *args):
		if self.ok:
			self._focus_out()

	def _color_widget(self):
		return self.entry.child
