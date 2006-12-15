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

import csv, StringIO

#
# TODO: make it works with references
#
def import_csv(csv_data, f, model, fields):
	fname = csv_data['fname']
	content = file(fname,'rb').read()
	input=StringIO.StringIO(content)
	data = list(csv.reader(input, quotechar=csv_data['del'], delimiter=csv_data['sep']))[int(csv_data['skip']):]
	datas = []
	#if csv_data['combo']:
	for line in data:
		datas.append(map(lambda x:x.decode(csv_data['combo']).encode('utf-8'), line))
	try:
		res = rpc.session.rpc_exec_auth('/object', 'execute', model, 'import_data', f, datas)
	except Exception, e:
		common.warning(str(e), _('XML-RPC error !'))
		return False
	if res[0]>=0:
		common.message(_('Imported %d objects !') % (res[0],))
	else:
		d = ''
		for key,val in res[1].items():
			d+= ('\t%s: %s\n' % (str(key),str(val)))
		error = u'Error trying to import this record:\n%s\nError Message:\n%s\n\n%s' % (d,res[2],res[3])
		common.message_box('Importation Error !', unicode(error))
	return True

class win_import(object):
	def __init__(self, model, fields, preload = []):
		self.glade = glade.XML(common.terp_path("terp.glade"),'win_import',gettext.textdomain())
		self.glade.get_widget('import_csv_combo').set_active(0)
		self.win = self.glade.get_widget('win_import')
		self.model = model
		self.fields_data = {}

		self.view1 = gtk.TreeView()
		self.view1.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
		self.glade.get_widget('import_vp_left').add(self.view1)
		self.view2 = gtk.TreeView()
		self.view2.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
		self.glade.get_widget('import_vp_right').add(self.view2)
		self.view1.set_headers_visible(False)
		self.view2.set_headers_visible(False)

		cell = gtk.CellRendererText()
		column = gtk.TreeViewColumn(_('Field name'), cell, text=0, background=2)
		self.view1.append_column(column)

		cell = gtk.CellRendererText()
		column = gtk.TreeViewColumn(_('Field name'), cell, text=0)
		self.view2.append_column(column)

		self.model1 = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
		self.model2 = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)

		for f in preload:
			self.model2.set(self.model2.append(), 0, f[1], 1, f[0])

		self.fields = {}
		self.fields_invert = {}
		def model_populate(fields, prefix_node='', prefix=None, prefix_value='', level=2):
			def str_comp(x,y):
				if x<y: return 1
				elif x>y: return -1
				else: return 0
			fields_order = fields.keys()
			fields_order.sort(lambda x,y: str_comp(fields[x].get('string', ''), fields[y].get('string', '')))
			for field in fields_order:
				if (fields[field]['type'] not in ('reference',)) and (not fields[field].get('readonly', False)):
					self.fields_data[prefix_node+field] = fields[field]
					st_name = prefix_value+fields[field]['string'] or field 
					node = self.model1.insert(prefix, 0, [st_name, prefix_node+field, (fields[field].get('required', False) and '#ddddff') or 'white'])
					self.fields[prefix_node+field] = st_name
					self.fields_invert[st_name] = prefix_node+field
					if fields[field]['type']=='one2many' and level>0:
						fields2 = rpc.session.rpc_exec_auth('/object', 'execute', fields[field]['relation'], 'fields_get', False, rpc.session.context)
						model_populate(fields2, prefix_node+field+'/', node, st_name+'/', level-1)
		model_populate(fields)

		#for f in fields:
		#	self.model1.set(self.model1.append(), 1, f, 0, fields[f].get('string', 'unknown'))

		self.view1.set_model(self.model1)
		self.view2.set_model(self.model2)
		self.view1.show_all()
		self.view2.show_all()

		self.glade.signal_connect('on_but_unselect_all_clicked', self.sig_unsel_all)
		self.glade.signal_connect('on_but_select_all_clicked', self.sig_sel_all)
		self.glade.signal_connect('on_but_select_clicked', self.sig_sel)
		self.glade.signal_connect('on_but_unselect_clicked', self.sig_unsel)
		self.glade.signal_connect('on_but_autodetect_clicked', self.sig_autodetect)

	def sig_autodetect(self, widget=None):
		fname= self.glade.get_widget('import_csv_file').get_filename()
		if not fname:
			common.message('You must select an import file first !')
			return True
		csvsep= self.glade.get_widget('import_csv_sep').get_text()
		csvdel= self.glade.get_widget('import_csv_del').get_text()
		csvcode= self.glade.get_widget('import_csv_combo').get_active_text() or 'UTF-8'

		self.glade.get_widget('import_csv_skip').set_value(1)
		try:
			data = csv.reader(file(fname), quotechar=csvdel, delimiter=csvsep)
		except:
			common.warning('Error opening .CSV file', 'Input Error.')
			return True
		self.sig_unsel_all()
		word=''
		try:
			for line in data:
				for word in line:
					word=word.decode(csvcode).encode('utf-8')
					num = self.model2.append()
					self.model2.set(num, 0, word, 1, self.fields_invert[word])
				break
		except:
			common.warning('Error processing your first line of the file.\nField %s is unknown !' % (word,), 'Import Error.')
		return True

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
		def _sig_sel_del(store, path, iter):
			store.remove(iter)
		(store,paths) = self.view2.get_selection().get_selected_rows()
		for p in paths:
			store.remove(store.get_iter(p))

	def sig_unsel_all(self, widget=None):
		self.model2.clear()

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

			csv = {
				'fname': self.glade.get_widget('import_csv_file').get_filename(),
				'sep': self.glade.get_widget('import_csv_sep').get_text(),
				'del': self.glade.get_widget('import_csv_del').get_text(),
				'skip': self.glade.get_widget('import_csv_skip').get_value(),
				'combo': self.glade.get_widget('import_csv_combo').get_active_text() or 'UTF-8'
			}
			self.win.destroy()
			if csv['fname']:
				return import_csv(csv, fields, self.model, self.fields)
			return False
		else:
			self.win.destroy()
			return False

