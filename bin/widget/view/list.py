##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
			f = lambda x,y: cmp(x[name].get_client(), y[name].get_client())
		else:
			f = lambda x,y: -1 * cmp(x[name].get_client(), y[name].get_client())
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
	
class ViewList(object):

	def __init__(self, screen, widget, children={}, buttons={}, toolbar=None):
		self.store = None
		self.screen = screen
		self.view_type = 'tree'
		self.model_add_new = True
		self.widget = widget
		self.widget.screen = screen

		self.display()

		self.widget.connect('button-press-event', self.__hello)
		self.widget.connect_after('row-activated', self.__sig_switch)
		selection = self.widget.get_selection()
		selection.connect('changed', self.__select_changed)

	def __hello(self, treeview, event, *args):
		if event.button==3:
			path = treeview.get_path_at_pos(int(event.x),int(event.y))
			selection = treeview.get_selection()
			model, iter = selection.get_selected()
			if (not path) or not path[0]:
				return False
			m = model.models[path[0][0]]
			if path[1]._type=='many2one':
				value = m[path[1].name].get()
				menu = gtk.Menu()
				finfo = self.screen.fields[path[1].name]
				fields_id = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.model.fields', 'search',[('relation','=',finfo['relation']),('ttype','=','many2one'),('relate','=',True)])
				fields = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.model.fields', 'read', fields_id, ['name','model_id'], rpc.session.context)
				models_id = [x['model_id'][0] for x in fields if x['model_id']]
				fields = dict(map(lambda x: (x['model_id'][0], x['name']), fields))
				models = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.model', 'read', models_id, ['name','model'], rpc.session.context)
				for model in models:
					field = fields[model['id']]
					model_name = model['model']
					item = gtk.ImageMenuItem('... '+model['name'])
					f = lambda model_name,field,value: lambda x: self._click_and_relate(model_name,field,value)
					item.connect('activate', f(model_name,field,value) )
					item.set_sensitive(bool(value))
					item.show()
					menu.append(item)
				menu.popup(None,None,None,event.button,event.time)

	def _click_and_relate(self, model, field, value):
		ids = rpc.session.rpc_exec_auth('/object', 'execute', model, 'search',[(field,'=',value)])
		obj = service.LocalService('gui.window')
		#view_ids = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.ui.view', 'search', [('model','=',model),('type','=','form')])
		obj.create(False, model, ids, [(field,'=',value)], 'form', None, mode='tree,form')
		return True


	def signal_record_changed(self, signal, *args):
		if not self.store:
			return
		if signal=='record-added':
			self.store.added(*args)
		elif signal=='record-removed':
			self.store.removed(*args)
		else:
			assert False, 'Unknown Signal !'

	def cancel(self):
		pass

	def __str__(self):
		return 'ViewList (%s)' % self.screen.resource

	def __getitem__(self, name):
		return None

	def destroy(self):
		self.widget.destroy()
		del self.screen
		del self.widget

	def __sig_switch(self, treeview, *args):
		self.screen.row_activate(self.screen)

	def __select_changed(self, tree_sel):
		if tree_sel.get_mode() == gtk.SELECTION_SINGLE:
			model, iter = tree_sel.get_selected()
			if iter:
				path = model.get_path(iter)[0]
				self.screen.current_model = model.models[path]

	def set_value(self):
		if self.widget.editable:
			self.widget.set_value()

	def reset(self):
		pass
	#
	# self.widget.set_model(self.store) could be removed if the store
	# has not changed -> better ergonomy. To test
	#
	def display(self):
		if (not self.widget.get_model()) or self.screen.models<>self.widget.get_model().model_group:
			self.store = AdaptModelGroup(self.screen.models)
			self.widget.set_model(self.store)
		if self.screen.current_model:
			path = self.store.on_get_path(self.screen.current_model)
			self.widget.set_cursor(path, self.widget.get_columns()[0], bool(self.widget.editable))
		else:
			#
			# Should find a simpler solution to do something like
			#self.widget.set_cursor(None,None,False)
			#
			if self.store:
				self.widget.set_model(self.store)

	def sel_ids_get(self):
		def _func_sel_get(store, path, iter, ids):
			model = store.on_get_iter(path)
			if model.id:
				ids.append(model.id)
		ids = []
		sel = self.widget.get_selection()
		sel.selected_foreach(_func_sel_get, ids)
		return ids

	def on_change(self, callback):
		self.set_value()
		self.screen.on_change(callback)

	def unset_editable(self):
		self.widget.editable = False
		for col in self.widget.get_columns():
			for renderer in col.get_cell_renderers():
				renderer.set_property('editable', False)

