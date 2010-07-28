# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import os
import sys
import tempfile
import time
from datetime import datetime
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

        self.widget = gtk.HBox(spacing=3)
        self.wid_text = gtk.Entry()
        #self.wid_text.set_property('activates_default', True)
        self.wid_text.set_property('editable', False)
        self.widget.pack_start(self.wid_text, expand=True, fill=True)

        self.filters = attrs.get('filters', None)
        if self.filters:
            self.filters = self.filters.split(',')

        class binButton(gtk.Button):
            def __init__(self, stock, title, long=True):
                assert stock is not None
                super(binButton, self).__init__()

                box = gtk.HBox()
                box.set_spacing(2)

                img = gtk.Image()
                img.set_from_stock(stock, gtk.ICON_SIZE_BUTTON)
                box.pack_start(img, expand=False, fill=False)

                if long:
                    label = gtk.Label(title)
                    label.set_use_underline(False)
                    box.pack_end(label, expand=False, fill=False)
                else:
                    self.set_relief(gtk.RELIEF_NONE)
                    if gtk.pygtk_version >= (2, 12, 0):
                        self.set_property('tooltip-text', title)

                self.add(box)

        self.but_select = binButton('terp-folder-orange', _('Select'), True)
        self.but_select.connect('clicked', self.sig_select)
        self.widget.pack_start(self.but_select, expand=False, fill=False)

        self.but_exec = binButton('terp-folder-blue', _('Open'), True)
        self.but_exec.connect('clicked', self.sig_execute)
        self.widget.pack_start(self.but_exec, expand=False, fill=False)

        self.but_save_as = binButton('gtk-save-as', _('Save As'), True)
        self.but_save_as.connect('clicked', self.sig_save_as)
        self.widget.pack_start(self.but_save_as, expand=False, fill=False)

        self.but_remove = binButton('gtk-clear', _('Clear'), True)
        self.but_remove.connect('clicked', self.sig_remove)
        self.widget.pack_start(self.but_remove, expand=False, fill=False)

	if attrs.get('signature') or True:
		self.but_sign = binButton('gtk-edit', _('Sign'), False)
		self.but_sign.connect('clicked', self.sig_sign)
		self.widget.pack_start(self.but_sign, expand=False, fill=False)

		self.but_verify = binButton('search', _('Verify'), False)
		self.but_verify.connect('clicked', self.sig_verify)
		self.widget.pack_start(self.but_verify, expand=False, fill=False)

        self.model_field = False
        self.has_filename = attrs.get('filename')
        self.data_field_name = attrs.get('name')
        self.__ro = False

    def _readonly_set(self, value):
        self.__ro = value
        if value:
            self.but_select.hide()
            self.but_remove.hide()
        else:
            self.but_select.show()
            self.but_remove.show()

    def _get_filename(self):
        return self._view.model.value.get(self.has_filename) \
               or self._view.model.value.get('name', self.data_field_name) \
               or datetime.now().strftime('%c')

    def sig_execute(self,widget=None):
        try:
            filename = self._get_filename()
            if filename:
                data = self._view.model.value.get(self.data_field_name)
                if not data:
                    data = self._view.model.get(self.data_field_name)[self.data_field_name]
                    if not data:
                        raise Exception(_("Unable to read the file data"))

                ext = os.path.splitext(filename)[1][1:]
                (fileno, fp_name) = tempfile.mkstemp('.'+ext, 'openerp_')

                os.write(fileno, base64.decodestring(data))
                os.close(fileno)

                printer.printer.print_file(fp_name, ext, preview=True)
        except Exception, ex:
            common.message(_('Error reading the file: %s') % str(ex))
            raise

    def sig_select(self, widget=None):
        try:
            # Add the filename from the field with the filename attribute in the view
            filters = []
            if not self.filters:
                filter_file = gtk.FileFilter()
                filter_file.set_name(_('All Files'))
                filter_file.add_pattern('*')
                filters.append(filter_file)
            else:
                for pat in self.filters:
                    filter_file = gtk.FileFilter()
                    filter_file.set_name(str(pat))
                    filter_file.add_pattern(pat)
                    filters.append(filter_file)

            filename = common.file_selection(_('Select a file...'), parent=self._window,filters=filters)
            if filename:
                self.model_field.set_client(self._view.model, base64.encodestring(file(filename, 'rb').read()))
                if self.has_filename:
                    self._view.model.set({self.has_filename: os.path.basename(filename)}, modified=True)
                self._view.display(self._view.model)
        except Exception, ex:
            common.message(_('Error reading the file: %s') % str(ex))

    def sig_save_as(self, widget=None):
        try:
            data = self._view.model.value.get(self.data_field_name)
            if not data:
                data = self._view.model.get(self.data_field_name)[self.data_field_name]
                if not data:
                    raise Exception(_("Unable to read the file data"))

            # Add the filename from the field with the filename attribute in the view
            filename = common.file_selection(
                _('Save As...'),
                parent=self._window,
                action=gtk.FILE_CHOOSER_ACTION_SAVE,
                filename=self._get_filename()
            )
            if filename:
                fp = file(filename,'wb+')
                fp.write(base64.decodestring(data))
                fp.close()
        except Exception, ex:
            common.message(_('Error writing the file: %s') % str(ex))

    def sig_remove(self, widget=None):
        self.model_field.set_client(self._view.model, False)
        if self.has_filename:
            self._view.model.set({self.has_filename: False}, modified=True)
        self.display(self._view.model, False)

    def sig_sign(self,widget=None):
	print "sign!"
	import subprocess
	from rpc import RPCProxy
	fp_name = False
	sig_name = False
        try:
	    if self._view.model.is_modified():
		common.message(_('Cannot sign a modified record. Please save it first!'))
		return False
            filename = self._get_filename()
            if filename:
                data = self._view.model.value.get(self.data_field_name)
                if not data:
                    data = self._view.model.get(self.data_field_name)[self.data_field_name]
                    if not data:
                        raise Exception(_("Unable to read the file data"))

                ext = os.path.splitext(filename)[1][1:]
                (fileno, fp_name) = tempfile.mkstemp('.'+ext, 'openerp_')

                os.write(fileno, base64.decodestring(data))
                os.close(fileno)
		r = common.sur_3b( _("Do you want to see the file first?\nFile is at %s\n\nPressing 'No' will sign anyway, 'Cancel' will not sign the file") % fp_name)
		if r == 'ok':
			printer.printer.print_file(fp_name, ext, preview=True)
		elif r == 'ko' or r == 'no':
			pass
		else:
			return False
		r = common.sur(_("Are you sure now that you want to sign this document?"))
		if not r :
			return False
		sig_name = fp_name+'.asc'
		# here, the batch mode will make sure that gpg will fail if the 
		# temporary file is atacked.
		res = subprocess.call(['gpg', '-ab','--batch', '-o', sig_name, fp_name], shell=False)
		# todo: get the stdout and print a better exception.
		if res > 0:
			raise Exception(_("GPG failed with code %d") % (res))
		elif res < 0:
			raise Exception(_("GPG terminated with signal %d") % (0-res))
		print "gpg finished"
		fp = file(sig_name,'rb')
		signature = fp.read()
		print "signature:",signature
		
		fid = self._view.model.id
		print "file id:",fid
		rpc = RPCProxy('document.signature')
		newsig = rpc.create( {'sig_type': 'gpg', 'file_id': fid, 'signature': signature })
		print "after create", newsig
		rpc.write([newsig],{'keyid':'<default>'})
		common.message(_("Document signed."))
		self._view.model.reload()
		
        except Exception, ex:
            common.message(_('Error signing the file: %s') % str(ex))
            raise
	finally:
		if fp_name:
			os.unlink(fp_name)
		if sig_name:
			os.unlink(sig_name)

    def sig_verify(self,widget=None):
        print "verify!"
	import subprocess
	from rpc import RPCProxy
	fp_name = False
	sig_name = False
        try:
	    if self._view.model.is_modified():
		common.message(_('Cannot verify a modified record. Please save it first!'))
		return False
            filename = self._get_filename()
            if filename:
                data = self._view.model.value.get(self.data_field_name)
                if not data:
                    data = self._view.model.get(self.data_field_name)[self.data_field_name]
                    if not data:
                        raise Exception(_("Unable to read the file data"))

		# First, download and save the file..
                ext = os.path.splitext(filename)[1][1:]
                (fileno, fp_name) = tempfile.mkstemp('.'+ext, 'openerp_')

                os.write(fileno, base64.decodestring(data))
                os.close(fileno)
		
		# Second, get all signatures:
		fid = self._view.model.id
		print "file id:",fid
		rpc = RPCProxy('document.signature')
		sigs = rpc.search( [ ('sig_type','=', 'gpg'), ('file_id','=', fid)])
		print "sigs:",sigs
		if not sigs or not len(sigs):
			common.message(_("No signatures found for file"))
			return None
		sig_results = []
		for sig in rpc.read(sigs,['keyid','signature','write_uid','write_date']):
			print "Checking:",sig
			(fsigno, fsigname) = tempfile.mkstemp('.'+ext+'.asc', 'openerp_')
			os.write(fsigno, sig['signature'])
			os.close(fsigno)
			rp = subprocess.Popen(['gpg', '--verify','--batch', fsigname, fp_name], 
				shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			(out,err) = rp.communicate()
			if rp.returncode == 0:
				resv = _("valid.")
			else:
				resv= _("INVALID!")
			print "res:",rp.returncode
			sig_results.append((sig, rp.returncode, resv, out, err))
			os.unlink(fsigname)
			fsigname = False
		print "gpg verifications finished"
		os.unlink(fp_name)
		fp_name = False
		
		msg = ""
		for sr in sig_results:
			wuid = sr[0]['write_uid'] and sr[0]['write_uid'][1] or '?'
			msg += _("\nSignature by %s[%s] at %s: %s\n%s\n") % \
				(wuid,sr[0]['keyid'],sr[0]['write_date'],sr[2],sr[4])
		
		common.message_box(_("Verification results"),msg)
		return True
		
        except Exception, ex:
            common.message(_('Error verifying the file: %s') % str(ex))
            raise
	finally:
		if fp_name:
			os.unlink(fp_name)
		if fsigname:
			os.unlink(fsigname)

    def display(self, model, model_field):
        def btn_activate(state):
            self.but_exec.set_sensitive(state)
            self.but_save_as.set_sensitive(state)
            self.but_remove.set_sensitive((not self.__ro) and state)

        if not model_field:
            self.wid_text.set_text('')
            btn_activate(False)
            return False
        super(wid_binary, self).display(model, model_field)
        self.model_field = model_field
        disp_text = model_field.get_client(model)

        self.wid_text.set_text(disp_text and str(disp_text) or '')
        btn_activate(bool(disp_text))
        return True

    def set_value(self, model, model_field):
        return

    def _color_widget(self):
        return self.wid_text

    def grab_focus(self):
        return self.wid_text.grab_focus()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

