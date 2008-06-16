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

import gobject
import gtk

import rpc
import service
import locale
from interface import parser_view


class AdaptModelGroup(gtk.GenericTreeModel):

	def __init__(self, model_group):
		super(AdaptModelGroup, self).__init__()
		self.model_group = model_group
		self.models = model_group.models
		self.last_sort = None
		self.sort_asc = True
		self.set_property('leak_references', False)

	def added(self, modellist, position):
		if modellist is self.models:
			model = self.models[position]
			self.emit('row_inserted', self.on_get_path(model),
					  self.get_iter(self.on_get_path(model)))

	def cancel(self):
		pass

	def changed_all(self, *args):
		self.emit('row_deleted', position)
		self.invalidate_iters()
	
	def removed(self, lst, position):
		self.emit('row_deleted', position)
		self.invalidate_iters()

	def append(self, model):
		self.model_group.model_add(model)

	def prepend(self, model):
		self.model_group.model_add(model, 0)
	
	def remove(self, iter):
		idx = self.get_path(iter)[0]
		self.model_group.model_remove(self.models[idx])
		self.invalidate_iters()

	def sort(self, name):
		self.sort_asc = not (self.sort_asc and (self.last_sort == name))
		self.last_sort = name
		if self.sort_asc:
			f = lambda x,y: cmp(x[name].get_client(x), y[name].get_client(y))
		else:
			f = lambda x,y: -1 * cmp(x[name].get_client(x), y[name].get_client(y))
		self.models.sort(f)
		for idx, row in enumerate(self.models):
			iter = self.get_iter(idx)
			self.row_changed(self.get_path(iter), iter)

	def saved(self, id):
		return self.model_group.writen(id)
		
	def __len__(self):
		return len(self.models)

	## Mandatory GenericTreeModel methods
	
	def on_get_flags(self):
		return gtk.TREE_MODEL_LIST_ONLY

	def on_get_n_columns(self):
		return 1

	def on_get_column_type(self, index):
		return gobject.TYPE_PYOBJECT
	
	def on_get_path(self, iter):
		return self.models.index(iter)

	def on_get_iter(self, path):
		if isinstance(path, tuple):
			path = path[0]
		if self.models:
			if path<len(self.models):
				return self.models[path]
			else:
				return None
		else:
			return None

	def on_get_value(self, node, column):
		assert column == 0
		return node

	def on_iter_next(self, node):
		try:
			return self.on_get_iter(self.on_get_path(node) + 1)
		except IndexError:
			return None
	
	def on_iter_has_child(self, node):
		return False

	def on_iter_children(self, node):
		return None

	def on_iter_n_children(self, node):
		return 0

	def on_iter_nth_child(self, node, n):
		if node is None and self.models:
			return self.on_get_iter(0)
		return None

	def on_iter_parent(self, node):
		return None
	
class ViewList(parser_view):

	def __init__(self, window, screen, widget, children=None, buttons=None,
			toolbar=None):
		super(ViewList, self).__init__(window, screen, widget, children,
				buttons, toolbar)
		self.store = None
		self.view_type = 'tree'
		self.model_add_new = True
		self.widget = gtk.VBox()
		self.widget_tree = widget
		scroll = gtk.ScrolledWindow()
		scroll.add(self.widget_tree)
		scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.widget.pack_start(scroll, expand=True, fill=True)
		self.widget_tree.screen = screen
		self.reload = False
		self.children = children

		if children:
			hbox = gtk.HBox()
			self.widget.pack_start(hbox, expand=False, fill=False, padding=2)
			for c in children:
				hbox2 = gtk.HBox()
				hbox2.pack_start(children[c][1], expand=True, fill=False)
				hbox2.pack_start(children[c][2], expand=True, fill=False)
				hbox.pack_start(hbox2, expand=False, fill=False, padding=12)
			hbox.show_all()

		self.display()

		self.widget_tree.connect('button-press-event', self.__hello)
		self.widget_tree.connect_after('row-activated', self.__sig_switch)
		selection = self.widget_tree.get_selection()
		selection.set_mode(gtk.SELECTION_MULTIPLE)
		selection.connect('changed', self.__select_changed)

	def __hello(self, treeview, event, *args):
		if event.button==3:
			path = treeview.get_path_at_pos(int(event.x),int(event.y))
			selection = treeview.get_selection()
			if selection.get_mode() == gtk.SELECTION_SINGLE:
				model, iter = selection.get_selected()
			elif selection.get_mode() == gtk.SELECTION_MULTIPLE:
				model, paths = selection.get_selected_rows()
			if (not path) or not path[0]:
				return False
			m = model.models[path[0][0]]

			# TODO: add menu cache
			if path[1]._type=='many2one':
				value = m[path[1].name].get(m)
				resrelate = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.values', 'get', 'action', 'client_action_relate', [(self.screen.fields[path[1].name]['relation'], False)], False, rpc.session.context)
				resrelate = map(lambda x:x[2], resrelate)
				menu = gtk.Menu()
				for x in resrelate:
					x['string'] = x['name']
					item = gtk.ImageMenuItem('... '+x['name'])
					f = lambda action, value, model: lambda x: self._click_and_relate(action, value, model)
					item.connect('activate', f(x, value, self.screen.fields[path[1].name]['relation']))
					item.set_sensitive(bool(value))
					item.show()
					menu.append(item)
				menu.popup(None,None,None,event.button,event.time)

	def _click_and_relate(self, action, value, model):
		data={}
		context={}
		act=action.copy()
		if not(value):
			common.message(_('You must select a record to use the relation !'))
			return False
		from widget.screen import Screen
		screen = Screen(model)
		screen.load([value])
		act['domain'] = screen.current_model.expr_eval(act['domain'], check_load=False)
		act['context'] = str(screen.current_model.expr_eval(act['context'], check_load=False))
		obj = service.LocalService('action.main')
		value = obj._exec_action(act, data, context)
		return value


	def signal_record_changed(self, signal, *args):
		if not self.store:
			return
		if signal=='record-added':
			self.store.added(*args)
		elif signal=='record-removed':
			self.store.removed(*args)
		else:
			pass
		self.update_children()

	def cancel(self):
		pass

	def __str__(self):
		return 'ViewList (%s)' % self.screen.resource

	def __getitem__(self, name):
		return None

	def destroy(self):
		self.widget_tree.destroy()
		del self.screen
		del self.widget_tree
		del self.widget

	def __sig_switch(self, treeview, *args):
		self.screen.row_activate(self.screen)

	def __select_changed(self, tree_sel):
		if tree_sel.get_mode() == gtk.SELECTION_SINGLE:
			model, iter = tree_sel.get_selected()
			if iter:
				path = model.get_path(iter)[0]
				self.screen.current_model = model.models[path]
		elif tree_sel.get_mode() == gtk.SELECTION_MULTIPLE:
			model, paths = tree_sel.get_selected_rows()
			if paths:
				self.screen.current_model = model.models[paths[0][0]]
		self.update_children()


	def set_value(self):
		if self.widget_tree.editable:
			self.widget_tree.set_value()

	def reset(self):
		pass
	#
	# self.widget.set_model(self.store) could be removed if the store
	# has not changed -> better ergonomy. To test
	#
	def display(self):
		if self.reload or (not self.widget_tree.get_model()) or self.screen.models<>self.widget_tree.get_model().model_group:
			self.store = AdaptModelGroup(self.screen.models)
			self.widget_tree.set_model(self.store)
		self.reload = False
		if not self.screen.current_model:
			#
			# Should find a simpler solution to do something like
			#self.widget.set_cursor(None,None,False)
			#
			if self.store:
				self.widget_tree.set_model(self.store)
		self.update_children()

	def update_children(self):
		ids = self.sel_ids_get()
		for c in self.children:
			value = 0.0
			for model in self.screen.models.models:
				if model.id in ids or not ids:
					value += model.fields_get()[self.children[c][0]].get(model, check_load=False)
			label_str = locale.format('%.' + str(self.children[c][3]) + 'f', value, True)
			if self.children[c][4]:
				self.children[c][2].set_markup('<b>%s</b>' % label_str)
			else:
				self.children[c][2].set_markup(label_str)

	def set_cursor(self, new=False):
		if self.screen.current_model:
			path = self.store.on_get_path(self.screen.current_model)
			focus_column = None
			for column in self.widget_tree.get_columns():
				renderer = column.get_cell_renderers()[0]
				if isinstance(renderer, gtk.CellRendererToggle):
					editable = renderer.get_property('activatable')
				else:
					editable = renderer.get_property('editable')
				if column.get_visible() and editable:
					focus_column = column
					break
			self.widget_tree.set_cursor(path, focus_column, new)

	def sel_ids_get(self):
		def _func_sel_get(store, path, iter, ids):
			model = store.on_get_iter(path)
			if model.id:
				ids.append(model.id)
		ids = []
		sel = self.widget_tree.get_selection()
		sel.selected_foreach(_func_sel_get, ids)
		return ids

	def sel_models_get(self):
		def _func_sel_get(store, path, iter, models):
			models.append(store.on_get_iter(path))
		models = []
		sel = self.widget_tree.get_selection()
		sel.selected_foreach(_func_sel_get, models)
		return models

	def on_change(self, callback):
		self.set_value()
		self.screen.on_change(callback)

	def unset_editable(self):
		self.widget_tree.editable = False
		for col in self.widget_tree.get_columns():
			for renderer in col.get_cell_renderers():
				if isinstance(renderer, gtk.CellRendererToggle):
					renderer.set_property('activatable', False)
				else:
					renderer.set_property('editable', False)

