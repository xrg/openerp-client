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
import xml.dom.minidom

from rpc import RPCProxy
import rpc

from widget.model.group import ModelRecordGroup

from widget.view.screen_container import screen_container
import widget_search

import signal_event
import tools

class Screen(signal_event.signal_event):
	def __init__(self, model_name, view_ids=[], view_type=['form','tree'], parent=None, context={}, views_preload={}, tree_saves=True, domain=[], create_new=False, row_activate=None, hastoolbar=False, default_get={}, show_search=False):
		super(Screen, self).__init__()
		self.show_search = show_search
		self.hastoolbar = hastoolbar
		self.default_get=default_get
		if not row_activate:
			self.row_activate = self.switch_view
		else:
			self.row_activate = row_activate
		self.create_new = create_new
		self.name = model_name
		self.domain = domain
		self.views_preload = views_preload
		self.resource = model_name
		self.rpc = RPCProxy(model_name)
		self.context = context
		self.context.update(rpc.session.context)
		self.views = []
		self.fields = {}
		self.view_ids = view_ids
		self.models = None
		self.parent=parent
		models = ModelRecordGroup(model_name, self.fields, parent=self.parent, context=self.context)
		self.models_set(models)
		self.current_model = None
		self.screen_container = screen_container()
		self.filter_widget = None
		self.widget = self.screen_container.widget_get()
		self.__current_view = 0
		self.tree_saves = tree_saves
		if view_type:
			self.view_to_load = view_type[1:]
			view_id = False
			if view_ids:
				view_id = view_ids.pop(0)
			view = self.add_view_id(view_id, view_type[0])
			self.screen_container.set(view.widget)

	def search_active(self, active=True):
		if active and self.show_search:
			if not self.filter_widget:
				view_form = rpc.session.rpc_exec_auth('/object', 'execute', self.name, 'fields_view_get', False, 'form', self.context)
				self.filter_widget = widget_search.form(view_form['arch'], view_form['fields'], self.name, self.parent)
				self.screen_container.add_filter(self.filter_widget.widget, self.search_filter, self.filter_widget.toggle, self.filter_widget.clear)
			self.screen_container.show_filter()
		else:
			self.screen_container.hide_filter()

	def search_filter(self, *args):
		v = self.filter_widget.value
		v_keys = map(lambda x: x[0], v)
		v += self.domain
		try:
			ids = rpc.session.rpc_exec_auth('/object', 'execute', self.name, 'search', v, 0, 400, 0, self.context)
		except:
			# Try if it is not an older server
			ids = rpc.session.rpc_exec_auth('/object', 'execute', self.name, 'search', v, 0, 400, 0)
		self.clear()
		self.load(ids)
		return True

	def models_set(self, models):
		import time
		c = time.time()
		if self.models:
			self.models.signal_unconnect(self.models)
		self.models = models
		self.parent = models.parent
		if len(models.models):
			self.current_model = models.models[0]
		else:
			self.current_model = None
		self.models.signal_connect(self, 'record-cleared', self._record_cleared)
		self.models.signal_connect(self, 'record-changed', self._record_changed)
		self.models.signal_connect(self, 'model-changed', self._model_changed)
		models.add_fields(self.fields, models)
		self.fields.update(models.fields)

	def _record_cleared(self, model_group, signal, *args):
		for view in self.views:
			view.reload = True

	def _record_changed(self, model_group, signal, *args):
		for view in self.views:
			view.signal_record_changed(signal[0], model_group.models, signal[1], *args)

	def _model_changed(self, model_group, model):
		if (not model) or (model==self.current_model):
			self.display()

	def _get_current_model(self):
		return self.__current_model

	#
	# Check more or less fields than in the screen !
	#
	def _set_current_model(self, value):
		self.__current_model = value
		try:
			pos = self.models.models.index(value)
		except:
			pos = -1
		self.signal('record-message', (pos, len(self.models.models or []), value and value.id))
		return True
	current_model = property(_get_current_model, _set_current_model)

	def destroy(self):
		for view in self.views:
			view.destroy()
			del view
		#del self.current_model
		self.models.signal_unconnect(self)
		del self.models
		del self.views

	def switch_view(self, screen=None):
		self.current_view.set_value()
		if self.current_model and self.current_model not in self.models.models:
			self.current_model = None
		if len(self.view_to_load):
			if self.view_ids:
				view_id = self.view_ids.pop(0)
				view_type = self.view_to_load.pop(0)
			else:
				view_id = False
				view_type = self.view_to_load.pop(0)
			self.add_view_id(view_id, view_type)
			self.__current_view = len(self.views) - 1
		else:
			self.__current_view = (self.__current_view + 1) % len(self.views)
			self.search_active(self.current_view.view_type in ('tree','graph'))
		widget = self.current_view.widget
		self.screen_container.set(self.current_view.widget)
		if self.current_model:
			self.current_model.validate_set()
		self.display()
		# TODO: set True or False accoring to the type

	def add_view_custom(self, arch, fields, display=False, toolbar={}):
		return self.add_view(arch, fields, display, True, toolbar=toolbar)

	def add_view_id(self, view_id, view_type, display=False):
		self.search_active(view_type in ('tree','graph'))
		if view_type in self.views_preload:
			return self.add_view(self.views_preload[view_type]['arch'], self.views_preload[view_type]['fields'], display, toolbar=self.views_preload[view_type].get('toolbar', False))
		else:
			view = self.rpc.fields_view_get(view_id, view_type, self.context, self.hastoolbar)
			return self.add_view(view['arch'], view['fields'], display, toolbar=view.get('toolbar', False))

	def add_view(self, arch, fields, display=False, custom=False, toolbar={}):
		def _parse_fields(node, fields):
			if node.nodeType == node.ELEMENT_NODE:
				if node.localName=='field':
					attrs = tools.node_attributes(node)
					if attrs.get('widget', False):
						if attrs['widget']=='one2many_list':
							attrs['widget']='one2many'
						attrs['type'] = attrs['widget']
					try:
						fields[str(attrs['name'])].update(attrs)
					except:
						raise
			for node2 in node.childNodes:
				_parse_fields(node2, fields)
		dom = xml.dom.minidom.parseString(arch)
		_parse_fields(dom, fields)

		from widget.view.widget_parse import widget_parse
		models = self.models.models
		if self.current_model and (self.current_model not in models):
			models = models + [self.current_model]
		if custom:
			self.models.add_fields_custom(fields, self.models)
		else:
			self.models.add_fields(fields, self.models)
		self.fields = self.models.fields

		parser = widget_parse(parent=self.parent)
		dom = xml.dom.minidom.parseString(arch)
		view = parser.parse(self, dom, self.fields, toolbar=toolbar)

		self.views.append(view)

		if display:
			self.__current_view = len(self.views) - 1
			self.current_view.display()
			self.screen_container.set(view.widget)
		return view

	def editable_get(self):
		return self.current_view.widget.editable

	def new(self, default=True, context={}):
		if self.current_view and self.current_view.view_type == 'tree' \
				and not self.current_view.widget.editable:
			self.switch_view()
		ctx = self.context.copy()
		ctx.update(context)
		model = self.models.model_new(default, self.domain, ctx)
		if (not self.current_view) or self.current_view.model_add_new or self.create_new:
			self.models.model_add(model, self.new_model_position())
		self.current_model = model
		self.current_model.validate_set()
		self.display()
		if self.current_view:
			self.current_view.set_cursor()
		return self.current_model

	def new_model_position(self):
		position = -1
		if self.current_view and self.current_view.view_type =='tree' \
				and self.current_view.widget.editable == 'top':
			position = 0
		return position

	def set_on_write(self, func_name):
		self.models.on_write = func_name

	def cancel_current(self):
		if self.current_model:
			self.current_model.cancel()
		if self.current_view:
			self.current_view.cancel()

	def save_current(self):
		if not self.current_model:
			return False
		self.current_view.set_value()
		id = False
		if self.current_model.validate():
			id = self.current_model.save(reload=True)
		else:
			self.current_view.display()
			self.current_view.set_cursor()
			return False
		if self.current_view.view_type == 'tree':
			for model in self.models.models:
				if model.is_modified():
					if model.validate():
						id = model.save(reload=True)
					else:
						self.current_model = model
						self.display()
						self.current_view.set_cursor()
						return False
			self.display()
			self.current_view.set_cursor()
		if self.current_model not in self.models:
			self.models.model_add(self.current_model)
		return id

	def _getCurrentView(self):
		if not len(self.views):
			return None
		return self.views[self.__current_view]
	current_view = property(_getCurrentView)

	def get(self):
		if not self.current_model:
			return None
		self.current_view.set_value()
		return self.current_model.get()

	def is_modified(self):
		if not self.current_model:
			return False
		self.current_view.set_value()
		res = False
		if self.current_view.view_type != 'tree':
			res = self.current_model.is_modified()
		else:
			for model in self.models.models:
				if model.is_modified():
					res = True
		return res

	def reload(self):
		self.current_model.reload()
		if self.parent:
			self.parent.reload()
		self.display()

	def remove(self, unlink = False):
		id = False
		if self.current_model:
			id = self.current_model.id
			idx = self.models.models.index(self.current_model)
			self.models.remove(self.current_model)
			if self.models.models:
				idx = min(idx, len(self.models.models)-1)
				self.current_model = self.models.models[idx]
			else:
				self.current_model = None
			if unlink and id:
				self.rpc.unlink([id])
			self.display()
			self.current_view.set_cursor()
		return id

	def load(self, ids):
		self.models.load(ids, display=False)
		self.current_view.reset()
		if ids:
			self.display(ids[0])
		else:
			self.current_model = None
			self.display()

	def display(self, res_id=None):
		if res_id:
			self.current_model = self.models[res_id]
		if self.views:
			self.current_view.display()
			self.current_view.widget.set_sensitive(bool(self.models.models or (self.current_view.view_type!='form') or self.current_model))

	def display_next(self):
		self.current_view.set_value()
		if self.current_model in self.models.models:
			idx = self.models.models.index(self.current_model)
			idx = (idx+1) % len(self.models.models)
			self.current_model = self.models.models[idx]
		else:
			self.current_model = len(self.models.models) and self.models.models[0]
		if self.current_model:
			self.current_model.validate_set()
		self.display()
		self.current_view.set_cursor()

	def display_prev(self):
		self.current_view.set_value()
		if self.current_model in self.models.models:
			idx = self.models.models.index(self.current_model)-1
			if idx<0:
				idx = len(self.models.models)-1
			self.current_model = self.models.models[idx]
		else:
			self.current_model = len(self.models.models) and self.models.models[-1]

		if self.current_model:
			self.current_model.validate_set()
		self.display()
		self.current_view.set_cursor()

	def sel_ids_get(self):
		return self.current_view.sel_ids_get()

	def id_get(self):
		return self.current_model.id

	def ids_get(self):
		return [x.id for x in self.models if x.id]

	def clear(self):
		self.models.clear()

	def on_change(self, callback):
		self.current_model.on_change(callback)
		self.display()

# vim:noexpandtab:
