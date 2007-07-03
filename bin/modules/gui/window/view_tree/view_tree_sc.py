##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import rpc
import gobject
import gtk

import gettext
import service

class view_tree_sc(object):
	def __init__(self, tree, model):
		self.model = model
		self.tree = tree
		self.tree.get_selection().set_mode('single')
		column = gtk.TreeViewColumn (_('ID'), gtk.CellRendererText(), text=0)
		self.tree.append_column(column)
		column.set_visible(False)
		cell = gtk.CellRendererText()

		column = gtk.TreeViewColumn (_('Description'), cell, text=1)
		self.tree.append_column(column)
		self.update()

	def update(self):
		store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
		uid =  rpc.session.uid
		try:
			sc = rpc.session.rpc_exec_auth_try('/object', 'execute', 'ir.ui.view_sc', 'get_sc', uid, self.model, rpc.session.context)
		except:
			sc = []
		for s in sc:
			num = store.append()
			store.set(num, 0, s['res_id'], 1, s['name'], 2, s['id'])
		self.tree.set_model(store)
		if self.model == 'ir.ui.menu':
			service.LocalService('gui.main').shortcut_set()

	def remove(self, id):
		self.update()
	def add(self, id):
		self.update()

	def value_get(self, col):
		sel = self.tree.get_selection().get_selected()
		if sel==None:
			return None
		(model, iter) = sel
		if not iter:
			return None
		return model.get_value(iter, col)

	def sel_id_get(self):
		res = self.value_get(0)
		if res!=None:
			return int(res)
		return None

	def serv_update(self, ids, action):
		if (action==2):
			self.update()

