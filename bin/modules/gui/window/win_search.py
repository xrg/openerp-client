##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#					Fabien Pinckaers <fp@tiny.Be>
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
import gobject
import gettext
import xmlrpclib
import win_list
import common

import rpc

from widget.screen import Screen
import widget_search

fields_list_type = {
	'checkbox': gobject.TYPE_BOOLEAN
}

class win_search(object):
	def __init__(self, model, sel_multi=True, ids=[], context={}, domain = [], parent=None):
		self.domain =domain
		self.context = context
		self.context.update(rpc.session.context)
		self.sel_multi = sel_multi
		self.glade = glade.XML(common.terp_path("terp.glade"),'win_search',gettext.textdomain())
		self.win = self.glade.get_widget('win_search')
		if parent:
			self.win.set_transient_for(parent)
		#self.glade.signal_connect('on_sea_but_find_clicked', self.find)

		self.screen = Screen(model, view_type=['tree'], context=context, parent=self.win)
		self.view = self.screen.current_view
		self.view.unset_editable()
		sel = self.view.widget.get_selection()

		if not sel_multi:
			sel.set_mode('single')
		else:
			sel.set_mode(gtk.SELECTION_MULTIPLE)
		vp = gtk.Viewport()
		vp.set_shadow_type(gtk.SHADOW_NONE)
		vp.add(self.screen.widget)
		sw = self.glade.get_widget('search_sw')
		sw.add(vp)
		sw.show_all()
		self.view.widget.connect('row_activated', self.sig_activate)
		self.view.widget.connect('button_press_event', self.sig_button)

		self.model_name = model

		view_form = rpc.session.rpc_exec_auth('/object', 'execute', self.model_name, 'fields_view_get', False, 'form', self.context)
		self.form = widget_search.form(view_form['arch'], view_form['fields'], model, parent=self.win)

		self.title = _('Tiny ERP Search: %s') % self.form.name
		self.title_results = _('Tiny ERP Search: %s (%%d result(s))') % self.form.name
		self.win.set_title(self.title)
		x, y = self.form.widget.size_request()
		#self.form.value = start_values

		hbox = self.glade.get_widget('search_hbox')
		hbox.pack_start(self.form.widget)
		self.ids = ids
		if self.ids:
			self.reload()
		self.old_search = None
		self.old_offset = self.old_limit = None
		if self.ids:
			self.old_search = []
			self.old_limit = self.glade.get_widget('search_spin_limit').get_value_as_int()
			self.old_offset = self.glade.get_widget('search_spin_offset').get_value_as_int()

		self.view.widget.show_all()
		if self.form.focusable:
			self.form.focusable.grab_focus()

	def sig_activate(self, treeview, path, column, *args):
		self.view.widget.emit_stop_by_name('row_activated')
		if not self.sel_multi:
			self.win.response(gtk.RESPONSE_OK)
		return False

	def sig_button(self, view, event):
		if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
			self.win.response(gtk.RESPONSE_OK)
		return False

	def find(self, widget=None, *args):
		limit = self.glade.get_widget('search_spin_limit').get_value_as_int()
		offset = self.glade.get_widget('search_spin_offset').get_value_as_int()
		if (self.old_search == self.form.value) and (self.old_limit==limit) and (self.old_offset==offset):
			self.win.response(gtk.RESPONSE_OK)
			return False
		self.old_offset = offset
		self.old_limit = limit
		v = self.form.value
		v_keys = map(lambda x: x[0], v)
		v += self.domain
		try:
			self.ids = rpc.session.rpc_exec_auth('/object', 'execute', self.model_name, 'search', v, offset, limit, 0, rpc.session.context)
		except:
			# Try if it is not an old server
			self.ids = rpc.session.rpc_exec_auth('/object', 'execute', self.model_name, 'search', v, offset, limit)
		self.reload()
		self.old_search = self.form.value
		self.win.set_title(self.title_results % len(self.ids))
		return True

	def reload(self):
		self.screen.clear()
		self.screen.load(self.ids)
		sel = self.view.widget.get_selection()
		if sel.get_mode() == gtk.SELECTION_MULTIPLE:
			sel.select_all()

	def sel_ids_get(self):
		return self.screen.sel_ids_get()

	def destroy(self):
		self.win.destroy()

	def go(self):
		end = False
		while not end:
			button = self.win.run()
			if button == gtk.RESPONSE_OK:
				res = self.sel_ids_get() or self.ids
				end = True
			elif button== gtk.RESPONSE_APPLY:
				end = not self.find()
				if end:
					res = self.sel_ids_get() or self.ids
			else:
				res = None
				end = True
		self.destroy()
		return res

# vim:noexpandtab:
