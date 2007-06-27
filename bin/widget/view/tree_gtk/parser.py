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

import re
import locale
import gtk
from gtk import glade
import math

import tools
from rpc import RPCProxy
from editabletree import EditableTreeView
from widget.view import interface

import time

from widget.view.form_gtk.many2one import dialog as M2ODialog
from modules.gui.window.win_search import win_search

import common
import rpc
import datetime as DT

def send_keys(renderer, editable, position, treeview):
	editable.connect('key_press_event', treeview.on_keypressed)
	editable.editing_done_id = editable.connect('editing_done', treeview.on_editing_done)

def sort_model(column, treeview):
	model = treeview.get_model()
	model.sort(column.name)

class parser_tree(interface.parser_interface):
	def parse(self, model, root_node, fields):
		dict_widget = {}
		attrs = tools.node_attributes(root_node)
		on_write = attrs.get('on_write', '')
		editable = attrs.get('editable', False)
		if editable:
			treeview = EditableTreeView(editable)
		else:
			treeview = gtk.TreeView()
		treeview.editable = editable
		treeview.colors = dict()
		self.treeview = treeview
		for color_spec in attrs.get('colors', '').split(';'):
			if color_spec:
				colour, test = color_spec.split(':')
				treeview.colors[colour] = test
		treeview.set_property('rules-hint', True)
		if not self.title:
			self.title = attrs.get('string', 'Unknown')

		for node in root_node.childNodes:
			node_attrs = tools.node_attributes(node)
			if node.localName == 'field':
				fname = str(node_attrs['name'])
				for boolean_fields in ('readonly', 'required'):
					if boolean_fields in node_attrs:
						node_attrs[boolean_fields] = bool(int(node_attrs[boolean_fields]))
				fields[fname].update(node_attrs)
				node_attrs.update(fields[fname])
				cell = Cell(fields[fname]['type'])(fname, treeview, node_attrs)
				renderer = cell.renderer
				if editable and not node_attrs.get('readonly', False):
					renderer.set_property('editable', True)
					renderer.connect_after('editing-started', send_keys, treeview)
#					renderer.connect_after('editing-canceled', self.editing_canceled)

				col = gtk.TreeViewColumn(fields[fname]['string'], renderer)
				col.name = fname
				col._type = fields[fname]['type']
				col.set_cell_data_func(renderer, cell.setter)
				col.set_clickable(True)
				twidth = {
					'integer': 60,
					'float': 80,
					'float_time': 80,
					'date': 70,
					'datetime': 120,
					'selection': 90,
					'char': 100,
					'one2many': 50,
					'many2many': 50,
				}
				if 'width' in fields[fname]:
					width = int(fields[fname]['width'])
				else:
					width = twidth.get(fields[fname]['type'], 100)
				col.set_min_width(width)
				col.connect('clicked', sort_model, treeview)
				col.set_resizable(True)
				#col.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
				col.set_visible(not fields[fname].get('invisible', False))
				n = treeview.append_column(col)
				if 'sum' in fields[fname] and fields[fname]['type'] in ('integer', 'float', 'float_time'):
					dict_widget[n] = (fname, gtk.Label(fields[fname]['sum']+': '), gtk.Label(0), fields.get('digits', (16,2))[1])
		return treeview, dict_widget, [], on_write

class UnsettableColumn(Exception):
	pass

class Cell(object):
	def __new__(self, type):
		klass = CELLTYPES.get(type, CELLTYPES['char'])
		return klass


class Char(object):
	def __init__(self, field_name, treeview=None, attrs={}):
		self.field_name = field_name
		self.attrs = attrs
		self.renderer = gtk.CellRendererText()
		self.treeview = treeview

	def setter(self, column, cell, store, iter):
		model = store.get_value(iter, 0)
		text = self.get_textual_value(model)
		cell.set_property('text', text)
		color = self.get_color(model)
		cell.set_property('foreground', str(color))
		if self.attrs['type'] in ('float', 'int'):
			align = 1
		else:
			align = 0
		if self.treeview.editable:
			if not model[self.field_name].state_attrs.get('valid', True):
				cell.set_property('background', common.colors.get('invalid', 'white'))
			elif bool(int(model[self.field_name].state_attrs.get('required', 0))):
				cell.set_property('background', common.colors.get('required', 'white'))
		cell.set_property('xalign', align)

	def get_color(self, model):
		to_display = ''
		for color, expr in self.treeview.colors.items():
			if model.expr_eval(expr, check_load=False):
				to_display = color
				break
		return to_display or 'black'

	def open_remote(self, model, create, changed=False, text=None):
		raise NotImplementedError

	def get_textual_value(self, model):
		return model[self.field_name].get_client(model) or ''

	def value_from_text(self, model, text):
		return text

class Int(Char):

	def value_from_text(self, model, text):
		return int(text)

class GenericDate(Char):

	def get_textual_value(self, model):
		value = model[self.field_name].get_client(model)
		if not value:
			return ''
		date = time.strptime(value, self.server_format)
		return time.strftime(self.display_format, date)

	def value_from_text(self, model, text):
		if not text:
			return False
		try:
			dt = time.strptime(text, self.display_format)
		except:
			try:
				dt = list(time.localtime())
				dt[2] = int(text)
				dt = tuple(dt)
			except:
				return False
		return time.strftime(self.server_format, dt)

if not hasattr(locale, 'nl_langinfo'):
	locale.nl_langinfo = lambda *a: '%x'

if not hasattr(locale, 'D_FMT'):
	locale.D_FMT = None

class Date(GenericDate):
	server_format = '%Y-%m-%d'
	display_format = locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y')

class Datetime(GenericDate):
	server_format = '%Y-%m-%d %H:%M:%S'
	display_format = locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y')+' %H:%M:%S'

	def get_textual_value(self, model):
		value = model[self.field_name].get_client(model)
		if not value:
			return ''
		date = time.strptime(value, self.server_format)
		if 'tz' in rpc.session.context:
			try:
				import pytz
				lzone = pytz.timezone(rpc.session.context['tz'])
				szone = pytz.timezone(rpc.session.timezone)
				dt = DT.datetime(date[0], date[1], date[2], date[3], date[4], date[5], date[6])
				sdt = szone.localize(dt, is_dst=True)
				ldt = sdt.astimezone(lzone)
				date = ldt.timetuple()
			except:
				pass
		return time.strftime(self.display_format, date)

	def value_from_text(self, model, text):
		if not text:
			return False
		try:
			date = time.strptime(text, self.display_format)
		except:
			try:
				dt = list(time.localtime())
				dt[2] = int(text)
				date = tuple(dt)
			except:
				return False
		if 'tz' in rpc.session.context:
			try:
				import pytz
				lzone = pytz.timezone(rpc.session.context['tz'])
				szone = pytz.timezone(rpc.session.timezone)
				dt = DT.datetime(date[0], date[1], date[2], date[3], date[4], date[5], date[6])
				ldt = lzone.localize(dt, is_dst=True)
				sdt = ldt.astimezone(szone)
				date = sdt.timetuple()
			except:
				pass
		return time.strftime(self.server_format, date)

class Float(Char):
	def get_textual_value(self, model):
		_, digit = self.attrs.get('digits', (16,2) )
		return locale.format('%.'+str(digit)+'f', model[self.field_name].get_client(model) or 0.0)

	def value_from_text(self, model, text):
		try:
			return locale.atof(text)
		except:
			return 0.0

from mx.DateTime import DateTimeDelta

class FloatTime(Char):
	def get_textual_value(self, model):
		val = model[self.field_name].get_client(model)
		t = '%02d:%02d' % (math.floor(abs(val)),round(abs(val)%1+0.01,2) * 60)
		if val<0:
			t = '-'+t
		_, digit = self.attrs.get('digits', (16,2) )
		return t

	def value_from_text(self, model, text):
		try:
			if text and ':' in text:
				return round(int(text.split(':')[0]) + int(text.split(':')[1]) / 60.0,2)
			else:
				return locale.atof(text)
		except:
			pass
		return 0.0

class M2O(Char):

	def value_from_text(self, model, text):
		if not text:
			return False

		relation = model[self.field_name].attrs['relation']
		rpc = RPCProxy(relation)

		domain = model[self.field_name].domain_get(model)
		context = model[self.field_name].context_get(model)

		names = rpc.name_search(text, domain, 'ilike', context)
		if len(names) != 1:
			return self.search_remote(relation, [x[0] for x in names],
							 domain=domain, context=context)[0]
		return names[0]

	def open_remote(self, model, create=True, changed=False, text=None):
		modelfield = model.mgroup.mfields[self.field_name]
		relation = modelfield.attrs['relation']
		
		domain=modelfield.domain_get(model)
		context=modelfield.context_get(model)
		if create:
			id = None
		elif not model.modified and not changed:
			id = modelfield.get(model)
		else:
			rpc = RPCProxy(relation)

			names = rpc.name_search(text, domain, 'ilike', context)
			if len(names) == 1:
				return True, names[0]
			searched = self.search_remote(relation, [x[0] for x in names], domain=domain, context=context)
			if searched[0]:
				return True, searched
			return False, False
		dia = M2ODialog(relation, id, domain=domain,context=context)
		new_value = dia.run()
		dia.destroy()
		if new_value[0]:
			return True, new_value[1]
		else:
			return False, False
	
	def search_remote(self, relation, ids=[], domain=[], context={}):
		rpc = RPCProxy(relation)

		win = win_search(relation, sel_multi=False, ids=ids, context=context, domain=domain)
		found = win.go()
		if found:
			return rpc.name_get([found[0]], context)[0]
		else:
			return False, None


class O2M(Char):
	def get_textual_value(self, model):
		return '( '+str(len(model[self.field_name].get_client(model).models)) + ' )'

	def value_from_text(self, model, text):
		raise UnsettableColumn('Can not set column of type o2m')


class M2M(Char):
	def get_textual_value(self, model):
		value = model[self.field_name].get_client(model)
		if value:
			return '(%s)' % len(value)
		else:
			return '(0)'

	def value_from_text(self, model, text):
		if not text:
			return []
		if not (text[0]<>'('):
			return model[self.field_name].get(model)
		relation = model[self.field_name].attrs['relation']
		rpc = RPCProxy(relation)
		domain = model[self.field_name].domain_get(model)
		context = model[self.field_name].context_get(model)
		names = rpc.name_search(text, domain, 'ilike', context)
		ids = [x[0] for x in names]
		win = win_search(relation, sel_multi=True, ids=ids, context=context, domain=domain)
		found = win.go()
		return found or []

	def open_remote(self, model, create=True, changed=False, text=None):
		modelfield = model[self.field_name]
		relation = modelfield.attrs['relation']

		rpc = RPCProxy(relation)
		context = model[self.field_name].context_get(model)
		domain = model[self.field_name].domain_get(model)
		if create:
			if text and len(text) and text[0]<>'(':
				domain.append(('name','=',text))
			ids = rpc.search(domain)
			if ids and len(ids)==1:
				return True, ids
		else:
			ids = model[self.field_name].get_client(model)
		win = win_search(relation, sel_multi=True, ids=ids, context=context, domain=domain)
		found = win.go()
		if found:
			return True, found
		else:
			return False, None

class Selection(Char):

	def __init__(self, *args):
		super(Selection, self).__init__(*args)
		self.renderer = gtk.CellRendererCombo()
		selection_data = gtk.ListStore(str, str)
		for x in self.attrs.get('selection', []):
			selection_data.append(x)
		self.renderer.set_property('model', selection_data)
		self.renderer.set_property('text-column', 1)

	def get_textual_value(self, model):
		selection = dict(model[self.field_name].attrs['selection'])
		return selection.get(model[self.field_name].get(model), '')

	def value_from_text(self, model, text):
		selection = model[self.field_name].attrs['selection']
		for val, txt in selection:
			if txt == text:
				return val
		return False

CELLTYPES = dict(char=Char,
				 many2one=M2O,
				 date=Date,
				 one2many=O2M,
				 many2many=M2M,
				 selection=Selection,
				 float=Float,
				 float_time=FloatTime,
				 int=Int,
				 datetime=Datetime)

# vim:noexpandtab:
