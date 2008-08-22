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

import os
import sys
import tempfile
import time

import base64

import gtk
import gettext

import rpc
import interface
import common
import options
import printer


class wid_binary(interface.widget_interface):
    def __init__(self, window, parent, model, attrs={}):
        interface.widget_interface.__init__(self, window, parent, model, attrs)

        self.widget = gtk.HBox(spacing=5)
        self.wid_text = gtk.Entry()
        self.wid_text.set_property('activates_default', True)
        self.widget.pack_start(self.wid_text, expand=True, fill=True)

        self.but_new = gtk.Button() 
        img = gtk.Image()
        img.set_from_stock( 'gtk-execute', gtk.ICON_SIZE_BUTTON )
        label = gtk.Label( ('_Open' ))
        label.set_use_underline( True )
        hbox = gtk.HBox()
        hbox.set_spacing( 2 )
        hbox.pack_start( img, expand=False, fill=False )
        hbox.pack_end( label, expand=False, fill=False )

        self.but_new.add( hbox )
        self.but_new.connect('clicked', self.sig_execute)
        self.widget.pack_start(self.but_new, expand=False, fill=False)

        self.but_new = gtk.Button() 
        img = gtk.Image()
        img.set_from_stock( 'gtk-open', gtk.ICON_SIZE_BUTTON )
        label = gtk.Label( _('_Select') )
        label.set_use_underline( True )
        hbox = gtk.HBox()
        hbox.set_spacing( 2 )
        hbox.pack_start( img, expand=False, fill=False )
        hbox.pack_end( label, expand=False, fill=False )

        self.but_new.add( hbox )
        self.but_new.connect('clicked', self.sig_select)
        self.widget.pack_start(self.but_new, expand=False, fill=False)

        self.but_save_as = gtk.Button(stock='gtk-save-as')
        self.but_save_as.connect('clicked', self.sig_save_as)
        self.widget.pack_start(self.but_save_as, expand=False, fill=False)

        self.but_remove = gtk.Button(stock='gtk-clear')
        self.but_remove.connect('clicked', self.sig_remove)
        self.widget.pack_start(self.but_remove, expand=False, fill=False)

        self.model_field = False
        self.has_filename = attrs.get( 'filename' )

    def _readonly_set(self, value):
        if value:
            self.but_new.hide()
            self.but_remove.hide()
        else:
            self.but_new.show()
            self.but_remove.show()

    def sig_execute(self,widget=None):
        try:
            filename = self._view.model.value.get( self.has_filename ) or self._view.model.value['name'] 
            if filename:
                id = int(self._view.model.get(includeid=True)['id'])
                data = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.attachment', 'read', [id])
                if not len(data):
                    return None
                ext = os.path.splitext( filename )[1][1:]
                (fileno, fp_name) = tempfile.mkstemp('.'+ext, 'tinyerp_')

                fp = file( fp_name, 'wb+')
                fp.write( base64.decodestring( data[0]['datas'] ) )
                fp.close()
                os.close(fileno)

                printer.printer.print_file( fp_name, ext, preview=True )
        except Exception, ex:
            common.message(_('Error reading the file'))

    def sig_select(self, widget=None):
        try:
            # Add the filename from the field with the filename attribute in the view
            filename = common.file_selection(_('Select a file...'), parent=self._window)
            if filename:
                self.model_field.set_client(self._view.model, base64.encodestring(file(filename, 'rb').read()))
                fname = self.attrs.get('fname_widget', False)
                filename = os.path.basename( filename )
                if fname:
                    self.parent.value = {fname:filename}
                self._view.model.set( { 'name': filename, 'title' : filename } )
                self._view.display(self._view.model) 
        except Exception, ex:
            common.message(_('Error reading the file'))

    def sig_save_as(self, widget=None):
        try:
            id = int(self._view.model.get(includeid=True)['id'])
            data = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.attachment', 'read', [id])
            if not len(data):
                return None
            # Add the filename from the field with the filename attribute in the view
            filename = common.file_selection(
                _('Save As...'),
                parent=self._window, 
                action=gtk.FILE_CHOOSER_ACTION_SAVE,
                filename=data[0]['name']
            )
            if filename:
                fp = file(filename,'wb+')
                fp.write(base64.decodestring(data[0]['datas']))
                fp.close()
        except:
            common.message(_('Error writing the file!'))

    def sig_remove(self, widget=None):
        self.model_field.set_client(self._view.model, False)
        fname = self.attrs.get('fname_widget', False)
        if fname:
            self.parent.value = {fname:False}
        self.display(self._view.model, self.model_field)

    def display(self, model, model_field):
        if not model_field:
            self.wid_text.set_text('')
            return False
        super(wid_binary, self).display(model, model_field)
        self.model_field = model_field
        self.wid_text.set_text(self._size_get(model_field.get(model)))
        return True

    def _size_get(self, l):
        return l and _('%d bytes') % len(l) or ''

    def set_value(self, model, model_field):
        return

    def _color_widget(self):
        return self.wid_text

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

