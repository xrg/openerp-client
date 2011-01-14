##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#						Fabien Pinckaers <fp@tiny.Be>
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
import copy

from view_tree import parse
import rpc
import common
import os
import base64
import gc
import urllib
import sys
import tempfile

class win_attach(object):
	def __init__(self, model, id):
		self.glade = glade.XML(common.terp_path("terp.glade"),'win_attach',gettext.textdomain())
		self.win = self.glade.get_widget('win_attach')
		self.ressource = (model, id)

		self.view = gtk.TreeView()
		hb = self.glade.get_widget('vp_attach')
		hb.add(self.view)

		self.view.get_selection().set_mode(gtk.SELECTION_SINGLE)
		self.view.connect('row_activated', self._sig_row_activated)

		view = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.attachment', 'fields_view_get', False, 'tree')

		p = parse.parse(view['fields'])
		p.parse(view['arch'], self.view)
		self.view.set_headers_visible(True)
		self.fields_order = p.fields_order

		types=[ gobject.TYPE_STRING ]
		for x in self.fields_order:
			types.append( gobject.TYPE_STRING)
		self.view_name = view['name']
		self.model_name = model
		self.model = gtk.ListStore(*types)


		self.view.set_model(self.model)
		self.view.show_all()
		self.reload()

		dict = {
			'on_attach_but_del_activate': self._sig_del,
			'on_attach_but_add_activate': self._sig_add,
			'on_attach_but_save_activate': self._sig_save,
			'on_attach_but_link_activate': self._sig_link,
			'comment_save': self._sig_comment,
		}
		for signal in dict:
			self.glade.signal_connect(signal, dict[signal])

	def _sig_comment(self, *args):
		start = self.glade.get_widget('attach_tv').get_buffer().get_start_iter()
		end = self.glade.get_widget('attach_tv').get_buffer().get_end_iter()
		comment = self.glade.get_widget('attach_tv').get_buffer().get_text(start, end)
		model,iter = self.view.get_selection().get_selected()
		context = copy.copy(rpc.session.context)
		if not iter:
			common.warning('You must put a text comment to an attachement.','Text not saved !')
			return None
		id = model.get_value(iter, 0)
		if id:
			rpc.session.rpc_exec_auth('/object', 'execute', 'ir.attachment', 'write', [int(id)], {'description':comment}, context)
		else:
			common.warning('You must put a text comment to an attachement.','Text not saved !')

	def _sig_del(self, *args):		
		model,iter = self.view.get_selection().get_selected()
		if not iter:
			return None
		id = model.get_value(iter, 0)
		if id:
			if common.sur(_('Are you sure you want to remove this attachment ?'), parent=self.win):
				rpc.session.rpc_exec_auth('/object', 'execute', 'ir.attachment', 'unlink', [int(id)])
		self.reload()

	def _sig_link(self, widget):
		filename = common.file_selection(_('Select the destination file'), parent=self.win)
		
		if not filename:
			return
		try:
			if filename:
				fname = os.path.basename(filename)
				id = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.attachment', 'create', {'name':fname, 'datas_fname':fname, 'res_model': self.ressource[0], 'res_id': self.ressource[1], 'link': filename})
				self.reload(preview=False)
				self.preview(id)
		except IOError, e:
			common.message(_('Can not open file !'))

	def _sig_save(self, id):
		model,iter = self.view.get_selection().get_selected()
		if not iter:
			return None
		id = model.get_value(iter, 0)
		if id:
			data = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.attachment', 'read', [id])
			if not len(data):
				return None
			filename = common.file_selection(_('Select the destination file'), filename=data[0]['datas_fname'], parent=self.win)
			if not filename:
				return None
			try:
				if not data[0]['link']:
					file(filename, 'wb+').write(base64.decodestring(data[0]['datas']))
				else:
					file(filename, 'wb+').write(urllib.urlopen(data[0]['link']).read())
			except IOError, e:
				common.message(_('Can not write file !'))

	def _sig_add(self, *args):
		dialog = gtk.FileChooserDialog("Open..",
			self.win,
			gtk.FILE_CHOOSER_ACTION_OPEN,
			(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
			gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		dialog.set_select_multiple(True)
		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		dialog.add_filter(filter)
		
		filter = gtk.FileFilter()
		filter.set_name("Images")
		for mime in ("image/png","image/jpeg","image/gif"):
			filter.add_mime_type(mime)
		for pat in ("*.png","*.jpg","*.gif","*.tif","*.xpm"):
			filter.add_pattern(pat)
		dialog.add_filter(filter)
		
		response = dialog.run()
		sfilenames = dialog.get_filenames()
		dialog.destroy()

		if response == gtk.RESPONSE_OK:
			try:
				for s in sfilenames:
					value = file(s,'rb').read()
					fname = os.path.basename(s)
					id = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.attachment', 'create', {'name':fname, 'datas':base64.encodestring(value), 'datas_fname':fname, 'res_model': self.ressource[0], 'res_id': self.ressource[1]})
				self.reload(preview=False)
				self.preview(id)
			except:
				pass

	def _sig_row_activated(self, *args):
		model,iters = self.view.get_selection().get_selected_rows()
		if not iters:
			return None
		id = model.get_value(model.get_iter(iters[0]), 0)
		self.preview(id)

	def preview(self, id):
		datas = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.attachment', 'read', [id])
		if not len(datas):
			return None
		datas = datas[0]

		buffer = self.glade.get_widget('attach_tv').get_buffer()
		buffer.delete(buffer.get_start_iter(), buffer.get_end_iter())
		iter_start = buffer.get_start_iter()
		buffer.insert(iter_start, datas['description'] or '')

		fname = str(datas['datas_fname'])
		label = self.glade.get_widget('attach_filename')
		label.set_text(fname)

		label = self.glade.get_widget('attach_title')
		label.set_text(str(datas['name']))

		decoder = {'jpg':'jpeg','jpeg':'jpeg','gif':'gif','png':'png'}
		ext = fname.split('.')[-1].lower()
		if ext in ('jpg', 'jpeg', 'png', 'gif'):
			try:
				if not datas['link']:
					dt = base64.decodestring(datas['datas'])
				else:
					dt = urllib.urlopen(datas['link']).read()

				def set_size(object, w, h):
					allocation = self.win.get_allocation()
					scale1 = 0.3*allocation.width / w
					scale2 = 0.3*allocation.height / h
					scale = min(scale1, scale2)
					object.set_size(int(scale*w), int(scale*h))

				loader = gtk.gdk.PixbufLoader (decoder[ext])
				loader.connect_after('size-prepared', set_size)
				
				loader.write (dt, len (dt))
				pixbuf = loader.get_pixbuf ()
				loader.close ()

				img = self.glade.get_widget('attach_image')
				img.set_from_pixbuf(pixbuf)
			except Exception, e:
				common.message(_('Unable to preview image file !\nVerify the format.'))
			gc.collect()
		elif ext in ('doc', 'xls', 'ppt', 'pdf'):
			if sys.platform in ['win32','nt']:
				fid, fname = tempfile.mkstemp(suffix='.'+ext)
				f = os.fdopen(fid, 'wb+')
				datas = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.attachment', 'read', [id])
				if not datas[0]['link']:
					if not len(datas):
						return None
					try:
						f.write(base64.decodestring(datas[0]['datas']))
					except IOError, e:
						common.message(_('Can not write file !'))
					f.close()
					os.startfile(fname)
				else:
					os.startfile(datas[0]['link'])
			else:
				self._sig_save(None)

	def reload(self, preview=True):
		self.model.clear()
		ids = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.attachment', 'search', [('res_model','=',self.ressource[0]), ('res_id', '=',self.ressource[1])])
		res_ids = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.attachment', 'read', ids, self.fields_order+['link'])
		for res in res_ids:
			num = self.model.append()
			args = []
			for x in range(len(self.fields_order)):
				args.append(x+1)
				if res['link']:
					args.append('link : '+res[self.fields_order[x]])
				else:
					args.append(res[self.fields_order[x]])
			self.model.set(num, 0, res['id'], *args)
		if preview and len(res_ids):
			self.preview(res_ids[0]['id'])

	def sel_ids_get(self):
		sel = self.view.get_selection()
		ids = []
		sel.selected_foreach(self._func_sel_get, ids)
		return ids

	def _func_sel(self, *args):
		if args[3][1]( args[0].get_value(args[2], args[3][2]), args[3][0]):
			args[3][3].select_iter(args[2])

	def _func_unsel(self, *args):
		if args[3][1]( args[0].get_value(args[2], args[3][2]), args[3][0]):
			args[3][3].unselect_iter(args[2])

	def _func_sel_get(self, *args):
		args[3].append(int(args[0].get_value(args[2], 0)))

	def go(self):
		end = False
		while not end:
			button = self.win.run()
			if button==gtk.RESPONSE_OK:
				res = self.sel_ids_get()
				end = True
			else:
				res = None
				end = True
		self.win.destroy()

