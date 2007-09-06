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

import base64
import gtk

import gettext

import interface
import os

import common

class wid_binary(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		interface.widget_interface.__init__(self, window, parent, model, attrs)

		self.widget = gtk.HBox(spacing=5)
		self.wid_text = gtk.Entry()
		self.wid_text.set_property('activates_default', True)
		self.widget.pack_start(self.wid_text, expand=True, fill=True)

		self.but_new = gtk.Button(stock='gtk-open')
		self.but_new.connect('clicked', self.sig_new)
		self.widget.pack_start(self.but_new, expand=False, fill=False)

		self.but_save_as = gtk.Button(stock='gtk-save-as')
		self.but_save_as.connect('clicked', self.sig_save_as)
		self.widget.pack_start(self.but_save_as, expand=False, fill=False)

		self.but_remove = gtk.Button(stock='gtk-clear')
		self.but_remove.connect('clicked', self.sig_remove)
		self.widget.pack_start(self.but_remove, expand=False, fill=False)

		self.model_field = False

	def _readonly_set(self, value):
		if value:
			self.but_new.hide()
			self.but_remove.hide()
		else:
			self.but_new.show()
			self.but_remove.show()

	def sig_new(self, widget=None):
		try:
			filename = common.file_selection(_('Select the file to attach'), parent=self._window)
			if filename:
				self.model_field.set_client(self._view.model,
						base64.encodestring(file(filename, 'rb').read()))
				fname = self.attrs.get('fname_widget', False)
				if fname:
					self.parent.value = {fname:os.path.basename(filename)}
				self.display(self._view.model, self.model_field)
		except:
			common.message(_('Error reading the file'))

	def sig_save_as(self, widget=None):
		try:
			filename = common.file_selection(_('Save attachment as...'), parent=self._window)
			if filename:
				fp = file(filename,'wb+')
				fp.write(base64.decodestring(self.model_field.get(self._view.model)))
				fp.close()
		except:
			common.message(_('Error writing the file!'))

	def sig_remove(self, widget=None):
		self.model_field.set_client(self._view.model, False)
		fname = self.attrs.get('fname_widget', False)
		if fname:
			self.parent.value = {fname:False}
		self.display(self._view.model, self.model_field)

	def display(self, model, model_field):
		if not model_field:
			self.wid_text.set_text('')
			return False
		super(wid_binary, self).display(model, model_field)
		self.model_field = model_field
		self.wid_text.set_text(self._size_get(model_field.get(model)))
		return True

	def _size_get(self, l):
		return l and _('%d bytes') % len(l) or ''

	def set_value(self, model, model_field):
		return

	def _color_widget(self):
		return self.wid_text
