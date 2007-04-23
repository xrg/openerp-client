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
from gtk import glade

import gettext

import interface
import wid_common
import form
import common
from many2one import dialog
from modules.gui.window.win_search import win_search

import rpc
from rpc import RPCProxy

class reference(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		interface.widget_interface.__init__(self, window, parent, model, attrs)
		self.win_gl = glade.XML(common.terp_path("terp.glade"),"widget_reference_model", gettext.textdomain())
		self.win_gl.signal_connect('on_reference_new_button_press', self.sig_new )
		self.win_gl.signal_connect('on_reference_edit_button_press', self.sig_edit )
		self.widget = self.win_gl.get_widget('widget_reference_model')

		self.widget_combo = self.win_gl.get_widget('reference_model')
		self.widget_combo.child.set_editable(False)
		self.set_popdown(attrs.get('selection',[]))

		self.win_gl.get_widget('but_reference_new').set_property('can-focus',False)
		self.win_gl.get_widget('but_reference_open').set_property('can-focus',False)

		self.wid_text = self.win_gl.get_widget('reference_entry')
		self.ok=True
		self.widget_combo.connect('changed', self.sig_changed_combo)
		self.wid_text.connect('changed', self.sig_changed)
		self.wid_text.connect('activate', self.sig_activate)
		self.wid_text.connect('button_press_event', self._menu_open)
		self.wid_text.connect('focus-out-event', lambda *a: self._focus_out())
		self.image_search = self.win_gl.get_widget('ref_image_search')
		self._value=None

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
		for l in lst:
			i = model.append()
			model.set(i, 0, l)
			self.widget_combo.child.set_text(l)
		# XXX this is a bug fix for gtk
		if gtk.widget_get_default_direction() == gtk.TEXT_DIR_RTL:
			self.widget_combo.child.set_alignment(1.0)
		else:
			self.widget_combo.child.set_alignment(0.0)
		self.widget_combo.set_model(model)
		self.widget_combo.set_text_column(0)
		return lst

	def _readonly_set(self, value):
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

	def sig_activate(self, *args):
		domain = self._view.modelfield.domain_get(self._view.model)
		context = self._view.modelfield.context_get(self._view.model)
		resource = self.get_model()

		ids = rpc.session.rpc_exec_auth('/object', 'execute', resource, 'name_search', self.wid_text.get_text(), domain, 'ilike', context)
		if len(ids)==1:
			id, name = ids[0]
			self._view.modelfield.set_client(self._view.model, (resource, (id, name)))
			self.display(self._view.model, self._view.modelfield)
			self.ok = True
			return True

		win = win_search(resource, sel_multi=False, ids=map(lambda x: x[0], ids), context=context, domain=domain)
		ids = win.go()
		if ids:
			id, name = rpc.session.rpc_exec_auth('/object', 'execute', resource, 'name_get', [ids[0]], rpc.session.context)[0]
			self._view.modelfield.set_client(self._view.model, (resource, (id, name)))
		self.display(self._view.model, self._view.modelfield)

	def sig_new(self, *args):
		dia = dialog(self.get_model())
		ok, value = dia.run()
		if ok:
			self._view.modelfield.set_client((self.get_model(), value))
			self.display(self._view.model, self._view.modelfield)
		dia.destroy()

	def sig_edit(self, *args):
		if self._value:
			model, (id, name) = self._value
			dia = dialog(model, id)
			ok, val = dia.run()
			dia.destroy()
		else:
			self.sig_activate()

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
		if value:
			model, (id, name) = value
			self.widget_combo.child.set_text(self._selection2[model])
			self.sig_changed()
			if not name:
				id, name = RPCProxy(model).name_get([id], rpc.session.context)[0]
			self._value = model, (id, name)
			self.wid_text.set_text(name)
			self.state_set('valid')
			self.image_search.set_from_stock('gtk-open',gtk.ICON_SIZE_BUTTON)
		else:
			self._value = False
			self.wid_text.set_text('')
			self.state_set('valid')
			self.image_search.set_from_stock('gtk-find',gtk.ICON_SIZE_BUTTON)
		self.ok = True

