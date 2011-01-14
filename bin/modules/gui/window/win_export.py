##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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
import common

import rpc
import sets

import service
import types
import os

def export_csv(fname, fields, result, write_title=False):
	import csv
	try:
		fp = file(fname, 'wb+')
		writer = csv.writer(fp)
		if write_title:
			writer.writerow(fields)
		for data in result:
			row = []
			for d in data:
				if type(d)==types.StringType:
					row.append(d.replace('\n',' ').replace('\t',' '))
				else:
					row.append(d)
			writer.writerow(row)
		fp.close()
		common.message(str(len(result))+_(' record(s) saved !'))
		return True
	except IOError, (errno, strerror):
		common.message(_("Operation failed !\nI/O error")+"(%s)" % (errno,))
		return False

def open_excel(fields, result):
	if os.name == 'nt':
		try:
			from win32com.client import Dispatch
			xlApp = Dispatch("Excel.Application")
			xlApp.Workbooks.Add()
			for col in range(len(fields)):
				xlApp.ActiveSheet.Cells(1,col+1).Value = fields[col]
			sht = xlApp.ActiveSheet
			for a in result:
				for b in range(len(a)):
					if type(a[b]) == type(''):
						a[b]=a[b].decode('utf-8','replace')
					elif type(a[b]) == type([]):
						if len(a[b])==2:
							a[b] = a[b][1].decode('utf-8','replace')
						else:
							a[b] = ''
			sht.Range(sht.Cells(2, 1), sht.Cells(len(result)+1, len(fields))).Value = result
			xlApp.Visible = 1
		except:
			common.error(_('Error Opening Excel !'),'')
	else:
		common.message(_("Function only available for MS Office !\nSorry, OOo users :("))

def datas_read(ids, model, fields, fields_view, prefix=''):
	datas = rpc.session.rpc_exec_auth('/object', 'execute', model, 'export_data', ids, fields)
	return datas
	rfield = []
	todo = {}
	for f in fields:
		res = f.split('.')
		if len(res)>1:
			todo.setdefault(res[0], []).append('.'.join(res[1:]))
			if not res[0] in rfield:
				rfield.append(res[0])
		else:
			if not f in rfield:
				rfield.append(f)

	datas = rpc.session.rpc_exec_auth('/object', 'execute', model, 'read', ids, rfield)
	for t in todo:
		ids2 = []
		for d in datas:
			if fields_view[prefix+t]['type'] in ('one2many', 'many2many'):
				ids2.extend(d[t])
			elif fields_view[prefix+t]['type'] in ('many2one', 'one2one'):
				if d[t]:
					ids2.append(d[t][0])
			else:
				ids2.append(d[t])
		datas2 = datas_read(ids2, fields_view[prefix+t]['relation'], todo[t], fields_view, prefix+t+'.')
		res = {}
		for d in datas2:
			res[d['id']] = {}
			for k in d:
				if k!='id':
					res[d['id']][t+'.'+k]=d[k]
		for d in datas:
			if fields_view[prefix+t]['type'] in ('one2many', 'many2many','many2one','one2one'):
				d.update(res.get(d[t] and d[t][0],{}))
			else:
				d.update(res.get(d[t],{}))
	return datas

class win_export(object):
	def __init__(self, model, ids, fields, preload = [], parent=None):
		self.glade = glade.XML(common.terp_path("terp.glade"), 'win_save_as', gettext.textdomain())
		self.win = self.glade.get_widget('win_save_as')
		if parent:
			self.win.set_transient_for(parent)
		self.ids = ids
		self.model = model
		self.fields_data = {}

		self.view1 = gtk.TreeView()
		self.view1.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
		self.glade.get_widget('exp_vp1').add(self.view1)
		self.view2 = gtk.TreeView()
		self.view2.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
		self.glade.get_widget('exp_vp2').add(self.view2)
		self.view1.set_headers_visible(False)
		self.view2.set_headers_visible(False)

		cell = gtk.CellRendererText()
		column = gtk.TreeViewColumn('Field name', cell, text=0)
		self.view1.append_column(column)

		cell = gtk.CellRendererText()
		column = gtk.TreeViewColumn('Field name', cell, text=0)
		self.view2.append_column(column)

		self.model1 = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
		self.model2 = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)

		for f in preload:
			self.model2.set(self.model2.append(), 0, f[1], 1, f[0])

		self.fields = {}
		def model_populate(fields, prefix_node='', prefix=None, prefix_value='', level=2):
			fields_order = fields.keys()
			fields_order.sort(lambda x,y: -cmp(fields[x].get('string', ''), fields[y].get('string', '')))
			for field in fields_order:
				self.fields_data[prefix_node+field] = fields[field]
				if prefix_node:
					self.fields_data[prefix_node + field]['string'] = '%s%s' % (prefix_value, self.fields_data[prefix_node + field]['string'])
				st_name = fields[field]['string'] or field 
				node = self.model1.insert(prefix, 0, [st_name, prefix_node+field])
				self.fields[prefix_node+field] = st_name
				if fields[field].get('relation', False) and level>0:
					fields2 = rpc.session.rpc_exec_auth('/object', 'execute', fields[field]['relation'], 'fields_get', False, rpc.session.context)
					model_populate(fields2, prefix_node+field+'/', node, st_name+'/', level-1)
		model_populate(fields)

		self.view1.set_model(self.model1)
		self.view2.set_model(self.model2)
		self.view1.show_all()
		self.view2.show_all()

		self.wid_action = self.glade.get_widget('win_saveas_combo')
		self.wid_write_field_names = self.glade.get_widget('add_field_names_cb')
		action = self.wid_action.set_active(os.name!='nt')

		self.glade.signal_connect('on_but_unselect_all_clicked', self.sig_unsel_all)
		self.glade.signal_connect('on_but_select_all_clicked', self.sig_sel_all)
		self.glade.signal_connect('on_but_select_clicked', self.sig_sel)
		self.glade.signal_connect('on_but_unselect_clicked', self.sig_unsel)
		self.glade.signal_connect('on_but_predefined_clicked', self.add_predef)

		# Creating the predefined export view
		self.pref_export = gtk.TreeView()
		self.pref_export.append_column(gtk.TreeViewColumn('Export name', gtk.CellRendererText(), text=1))
		self.pref_export.append_column(gtk.TreeViewColumn('Exported fields', gtk.CellRendererText(), text=2))
		self.glade.get_widget('predefined_exports').add(self.pref_export)

		self.pref_export.connect("row-activated", self.sel_predef)

		# Fill the predefined export tree view and show everything
		self.fill_predefwin()
		self.pref_export.show_all()

	def sig_sel_all(self, widget=None):
		self.model2.clear()
		for field in self.fields.keys():
			self.model2.set(self.model2.append(), 0, self.fields[field], 1, field)

	def sig_sel(self, widget=None):
		sel = self.view1.get_selection()
		sel.selected_foreach(self._sig_sel_add)

	def _sig_sel_add(self, store, path, iter):
		num = self.model2.append()
		self.model2.set(num, 0, store.get_value(iter,0), 1, store.get_value(iter,1))

	def sig_unsel(self, widget=None):
		store, paths = self.view2.get_selection().get_selected_rows()
		for p in paths:
			store.remove(store.get_iter(p))

	def sig_unsel_all(self, widget=None):
		self.model2.clear()
	
	def fill_predefwin(self):
		self.predef_model = gtk.ListStore(gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_STRING)
		ir_export = rpc.RPCProxy('ir.exports')
		ir_export_line = rpc.RPCProxy('ir.exports.line')
		export_ids = ir_export.search([('resource', '=', self.model)])
		for export in ir_export.read(export_ids):
			fields = ir_export_line.read(export['export_fields'])
			self.predef_model.append(([f['name'] for f in fields], export['name'], ', '.join([self.fields_data[f['name']]['string'] for f in fields])))
		self.pref_export.set_model(self.predef_model)

	def add_predef(self, button):
		name = common.ask('What is the name of this export ?')
		if not name:
			return 
		ir_export = rpc.RPCProxy('ir.exports')
		iter = self.model2.get_iter_root()
		fields = []
		while iter:
			field_name = self.model2.get_value(iter, 1)
			fields.append(field_name)
			iter = self.model2.iter_next(iter)
		ir_export.create({'name' : name, 'resource' : self.model, 'export_fields' : [(0, 0, {'name' : f}) for f in fields]})
		self.predef_model.append((fields, name, ','.join([self.fields_data[f]['string'] for f in fields])))
	
	def sel_predef(self, treeview, path, column):
		self.model2.clear()
		for field in self.predef_model[path[0]][0]:
			self.model2.append((self.fields_data[field]['string'], field))

	def go(self):
		button = self.win.run()
		if button==gtk.RESPONSE_OK:
			fields = []
			fields2 = []
			iter = self.model2.get_iter_root()
			while iter:
				fields.append(self.model2.get_value(iter, 1))
				fields2.append(self.model2.get_value(iter, 0))
				iter = self.model2.iter_next(iter)
			action = self.wid_action.get_active()
			self.win.destroy()
			result = datas_read(self.ids, self.model, fields, self.fields_data)
			#result = []
			#for data in datas:
			#	result.append([data.get(f, '') for f in fields])

			if not action:
				open_excel(fields2, result)
			else:
				fname = common.file_selection(_('Export Data'))
		 		if fname:
					export_csv(fname, fields2, result, self.wid_write_field_names.get_active())
			return True
		else:
			self.win.destroy()
			return False



