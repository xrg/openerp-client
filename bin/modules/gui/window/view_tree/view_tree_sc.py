# -*- encoding: utf-8 -*-
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

import rpc
import gobject
import gtk

import gettext
import service

class view_tree_sc(object):
    ( COLUMN_RES_ID, COLUMN_NAME, COLUMN_ID ) = range(3)
    def __init__(self, tree, model):
        self.model = model
        self.tree = tree
        self.tree.connect( 'key-press-event', self.on_key_press_event )
        self.tree.get_selection().set_mode('single')
        column = gtk.TreeViewColumn (_('ID'), gtk.CellRendererText(), text=0)
        self.tree.append_column(column)
        column.set_visible(False)
        cell = gtk.CellRendererText()
        cell.connect( 'edited', self.on_cell_edited )

        column = gtk.TreeViewColumn (_('Description'), cell, text=1)
        self.tree.append_column(column)
        self.update()

    def on_cell_edited(self, cell, path_string, new_text):
        model = self.tree.get_model()
        iter = model.get_iter_from_string(path_string)
        old_text = model.get_value( iter, self.COLUMN_NAME )
        if old_text <> new_text:
            res_id = int( model.get_value( iter, self.COLUMN_ID ) )
            rpc.session.rpc_exec_auth('/object', 'execute', 'ir.ui.view_sc', 'write', res_id, { 'name' : new_text }, rpc.session.context )
            model.set(iter, self.COLUMN_NAME, new_text)

        cell.set_property( 'editable', False )

    def on_key_press_event( self, widget, event ):
        if event.keyval == gtk.keysyms.F2:
            column = self.tree.get_column( self.COLUMN_NAME )
            cell = column.get_cell_renderers()[0]
            cell.set_property( 'editable', True )

            selected_row = widget.get_selection().get_selected()
            if selected_row and selected_row[1]:
                (model, iter) = selected_row
                path = model.get_path( iter )
                self.tree.set_cursor_on_cell( path, column, cell, True )


    def update(self):
        store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
        uid =  rpc.session.uid
        sc = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.ui.view_sc', 'get_sc', uid, self.model, rpc.session.context) or []
        for s in sc:
            num = store.append()
            store.set(num, 
              self.COLUMN_RES_ID, s['res_id'], 
              self.COLUMN_NAME, s['name'], 
              self.COLUMN_ID, s['id']
            )
        self.tree.set_model(store)
        if self.model == 'ir.ui.menu':
            service.LocalService('gui.main').shortcut_set(sc)

    def remove(self, id):
        self.update()
    def add(self, id):
        self.update()

    def value_get(self, col):
        sel = self.tree.get_selection().get_selected()
        if not sel:
            return None
        (model, iter) = sel
        if not iter:
            return None
        return model.get_value(iter, col)

    def sel_id_get(self):
        res = self.value_get(0)
        res = eval(str(res))
        if res:
            return int(res[0])
        return None

    def serv_update(self, ids, action):
        if (action==2):
            self.update()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

