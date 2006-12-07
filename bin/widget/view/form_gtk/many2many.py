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

import gobject
import gtk
from gtk import glade

import copy

import wid_common
import common

from widget.screen import Screen
import interface

import rpc

from modules.gui.window.win_search import win_search

class many2many(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		interface.widget_interface.__init__(self, window, parent, model, attrs)

		self.win_gl = glade.XML(common.terp_path("terp.glade"),"widget_many2many")
		self.win_gl.signal_connect('on_m2m_but_add_pressed', self._sig_add )
		self.win_gl.signal_connect('on_m2m_but_remove_pressed', self._sig_remove )

		vbox = gtk.VBox(homogeneous=False, spacing=1)
		vbox.pack_start(self.win_gl.get_widget('widget_many2many'))

		# if attrs.get('view_data_tree'): ...
		self.screen = Screen(attrs['relation'], view_type=['tree'])

		self.win_gl.get_widget('scrolledwindow7').add_with_viewport(self.screen.widget)
		self.widget = vbox

		self.wid_text = self.win_gl.get_widget('ent_many2many')
		self.wid_text.connect('activate', self._sig_activate)
		self.wid_text.connect('button_press_event', self._menu_open)

		self.wid_but_add = self.win_gl.get_widget('m2m_but_add')
		self.wid_but_remove = self.win_gl.get_widget('m2m_but_remove')
		self.old = None

	def destroy(self):
		self.screen.destroy()
		self.widget.destroy()
		del self.widget

	def _menu_sig_default_set(self):
		self.set_value(self._view.modelfield)
		return super(many2many, self)._menu_sig_default_set()

	def _menu_sig_default(self, obj):
		res = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['model'], 'default_get', [self.attrs['name']])
		self.value = res.get(self.attrs['name'], False)

	def _sig_add(self, *args):
		domain = self._view.modelfield.domain_get()
		context = self._view.modelfield.context_get()

		ids = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['relation'], 'name_search', self.wid_text.get_text(), domain, 'ilike', context)
		ids = map(lambda x: x[0], ids)
		if len(ids)<>1:
			win = win_search(self.attrs['relation'], sel_multi=True, ids=ids)
			ids = win.go()

		self.screen.load(ids)
		self.screen.display()
		self.wid_text.set_text('')

	def _sig_remove(self, *args):
		self.screen.remove()
		self.screen.display()

	def _sig_activate(self, *args):
		self._sig_add()
	
	def _readonly_set(self, ro):
		self.wid_text.set_editable(not ro)
		self.wid_text.set_sensitive(not ro)
		self.wid_but_remove.set_sensitive(not ro)
		self.wid_but_add.set_sensitive(not ro)

	def display(self, model_field):
		super(many2many, self).display(model_field)
		ids = []
		if model_field:
			ids = model_field.get_client()
		if ids<>self.old:
			self.screen.clear()
			self.screen.load(ids)
			self.old = ids
		self.screen.display()
		return True

	def set_value(self, model_field):
		model_field.set_client([x.id for x in self.screen.models.models])

