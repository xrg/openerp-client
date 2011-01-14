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

import copy
import gettext

import gobject
import gtk

import gettext

import interface
import wid_common
import common
from many2one import dialog
from modules.gui.window.win_search import win_search

import rpc
from rpc import RPCProxy

class reference(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		interface.widget_interface.__init__(self, window, parent, model, attrs)

		self.widget = gtk.HBox(spacing=3)

		self.widget_combo = gtk.ComboBoxEntry()
		self.widget_combo.child.set_editable(False)
		self.widget_combo.child.connect('changed', self.sig_changed_combo)
		self.widget_combo.child.connect('key_press_event', self.sig_key_pressed)
		self.widget.pack_start(self.widget_combo, expand=False, fill=True)

		self.widget.pack_start(gtk.Label('-'), expand=False, fill=False)

		self.wid_text = gtk.Entry()
		self.wid_text.set_property('width-chars', 13)
		self.wid_text.connect('key_press_event', self.sig_key_press)
		self.wid_text.connect('button_press_event', self._menu_open)
		self.wid_text.connect_after('changed', self.sig_changed)
		self.wid_text.connect_after('activate', self.sig_activate)
		self.wid_text_focus_out_id = self.wid_text.connect_after('focus-out-event', self.sig_activate, True)
		self.widget.pack_start(self.wid_text, expand=True, fill=True)

		self.but_new = gtk.Button()
		img_new = gtk.Image()
		img_new.set_from_stock('gtk-new',gtk.ICON_SIZE_BUTTON)
		self.but_new.set_image(img_new)
		self.but_new.set_relief(gtk.RELIEF_NONE)
		self.but_new.connect('clicked', self.sig_new)
		self.but_new.set_alignment(0.5, 0.5)
		self.but_new.set_property('can-focus', False)
		self.widget.pack_start(self.but_new, expand=False, fill=False)

		self.but_open = gtk.Button()
		img_find = gtk.Image()
		img_find.set_from_stock('gtk-find',gtk.ICON_SIZE_BUTTON)
		img_open = gtk.Image()
		img_open.set_from_stock('gtk-open',gtk.ICON_SIZE_BUTTON)
		self.but_open.set_image(img_find)
		self.but_open.set_relief(gtk.RELIEF_NONE)
		self.but_open.connect('clicked', self.sig_edit)
		self.but_open.set_alignment(0.5, 0.5)
		self.but_open.set_property('can-focus', False)
		self.widget.pack_start(self.but_open, padding=2, expand=False, fill=False)

		tooltips = gtk.Tooltips()
		tooltips.set_tip(self.but_new, _('Create a new resource'))
		tooltips.set_tip(self.but_open, _('Search / Open a resource'))
		tooltips.enable()

		self.ok = True
		self._readonly = False
		self._value = False
		self.set_popdown(attrs.get('selection',[]))

		self.last_key = (None, 0)
		self.key_catalog = {}

	def get_model(self):
		res = self.widget_combo.child.get_text()
		return self._selection.get(res, False)

	def set_popdown(self, selection):
		model = gtk.ListStore(gobject.TYPE_STRING)
		self._selection={}
		self._selection2={}
		lst = []
		for (i,j) in selection:
			name = str(j)
			lst.append(name)
			self._selection[name]=i
			self._selection2[i]=name
		self.key_catalog = {}
		for l in lst:
			i = model.append()
			model.set(i, 0, l)
			if l:
				key = l[0].lower()
				self.key_catalog.setdefault(key,[]).append(i)
		self.widget_combo.set_model(model)
		self.widget_combo.set_text_column(0)
		return lst

	def _readonly_set(self, value):
		self._readonly = value
		interface.widget_interface._readonly_set(self, value)
		self.wid_text.set_editable(not value)
		self.wid_text.set_sensitive(not value)

	def _color_widget(self):
		return self.wid_text

	def set_value(self, model, model_field):
		return model_field.set_client(model, self._value)

	def _menu_sig_pref(self, obj):
		self._menu_sig_default_set()

	def _menu_sig_default(self, obj):
		res = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['model'], 'default_get', [self.attrs['name']])
		self.value = res.get(self.attrs['name'], False)

	def sig_activate(self, widget, event=None, leave=False):
		self.ok = False
		self.wid_text.disconnect(self.wid_text_focus_out_id)
		resource = self.get_model()
		if self._value:
			if not leave:
				model, (id, name) = self._value
				dia = dialog(model, id, window=self._window)
				ok, val = dia.run()
				dia.destroy()
		else:
			if not self._readonly and ( self.wid_text.get_text() or not leave):
				domain = self._view.modelfield.domain_get(self._view.model)
				context = self._view.modelfield.context_get(self._view.model)
		
				ids = rpc.session.rpc_exec_auth('/object', 'execute', resource, 'name_search', self.wid_text.get_text(), domain, 'ilike', context)
				if len(ids)==1:
					id, name = ids[0]
					self._view.modelfield.set_client(self._view.model, (resource, [id, name]))
					self.display(self._view.model, self._view.modelfield)
					self.ok = True
					return True

				win = win_search(resource, sel_multi=False, ids=map(lambda x: x[0], ids), context=context, domain=domain, parent=self._window)
				ids = win.go()
				if ids:
					id, name = rpc.session.rpc_exec_auth('/object', 'execute', resource, 'name_get', [ids[0]], rpc.session.context)[0]
					self._view.modelfield.set_client(self._view.model, (resource, [id, name]))
		self.wid_text_focus_out_id = self.wid_text.connect_after('focus-out-event', self.sig_activate, True)
		self.display(self._view.model, self._view.modelfield)
		self.ok=True

	def sig_new(self, *args):
		dia = dialog(self.get_model(), window=self._window)
		ok, value = dia.run()
		if ok:
			self._view.modelfield.set_client((self.get_model(), value))
			self.display(self._view.model, self._view.modelfield)
		dia.destroy()

	sig_edit = sig_activate

	def sig_key_press(self, widget, event, *args):
		if event.keyval==gtk.keysyms.F1:
			self.sig_new(widget, event)
		elif event.keyval==gtk.keysyms.F2:
			self.sig_activate(widget, event)
		return False

	def sig_changed_combo(self, *args):
		self.wid_text.set_text('')
		self._value = False

	def sig_changed(self, *args):
		if self.attrs.get('on_change',False) and self._value and self.ok:
			self.on_change(self.attrs['on_change'])
			interface.widget_interface.sig_changed(self)
		elif self.ok:
			if self._view.modelfield.get(self._view.model):
				self._view.modelfield.set_client(self._view.model, False)
				self.display(self._view.model, self._view.modelfield)

	def display(self, model, model_field):
		if not model_field:
			self.widget_combo.child.set_text('')
			return False
		super(reference, self).display(model, model_field)
		value = model_field.get_client(model)
		self.ok = False
		img = gtk.Image()
		if value:
			model, (id, name) = value
			self.widget_combo.child.set_text(self._selection2[model])
			self.sig_changed()
			if not name:
				id, name = RPCProxy(model).name_get([id], rpc.session.context)[0]
			self._value = model, [id, name]
			self.wid_text.set_text(name)
			img.set_from_stock('gtk-open',gtk.ICON_SIZE_BUTTON)
			self.but_open.set_image(img)
		else:
			self._value = False
			self.wid_text.set_text('')
			img.set_from_stock('gtk-find',gtk.ICON_SIZE_BUTTON)
			self.but_open.set_image(img)
		self.ok = True

	def sig_key_pressed(self, *args):
		key = args[1].string.lower()
		if self.last_key[0] == key:
			self.last_key[1] += 1
		else:
			self.last_key = [ key, 1 ]
		if not self.key_catalog.has_key(key):
			return
		self.entry.set_active_iter(self.key_catalog[key][self.last_key[1] % len(self.key_catalog[key])])

