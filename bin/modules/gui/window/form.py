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

import types
import gettext

import gtk
import gobject
from gtk import glade

import rpc
import win_selection
import win_preference
import win_search
import win_export
import win_import
import win_list

import common
import service
import options
import copy

import gc

from observator import oregistry
from widget.screen import Screen

class form(object):
	def __init__(self, model, res_id=False, domain=[], view_type=None, view_ids=[], window=None, context={}, name=False):
		if not view_type:
			view_type = ['form','tree']
		else:
			if view_type[0] in ('tree','graph') and not res_id:
				res_id = rpc.session.rpc_exec_auth('/object', 'execute', model, 'search', domain)

		fields = {}
		self.model = model
		self.window = window
		self.previous_action = None
		self.glade = glade.XML(common.terp_path("terp.glade"),'win_form_container',gettext.textdomain())
		self.widget = self.glade.get_widget('win_form_container')
		self.widget.show_all()
		self.fields = fields
		self.domain = domain
		self.context = context

		self.screen = Screen(self.model, view_type=view_type, context=self.context, view_ids=view_ids, domain=domain, hastoolbar=options.options['form.toolbar'], show_search=True, parent=self.window)
		self.screen.signal_connect(self, 'record-message', self._record_message)
		oregistry.add_receiver('misc-message', self._misc_message)

		if not name:
			self.name = self.screen.current_view.title
		else:
			self.name = name
		vp = gtk.Viewport()
		vp.set_shadow_type(gtk.SHADOW_NONE)
		vp.add(self.screen.widget)
		self.sw = gtk.ScrolledWindow()
		self.sw.set_shadow_type(gtk.SHADOW_NONE)
		self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.sw.add(vp)
		self.sw.show_all()
		
		self.has_backup = False
		self.backup = {}

		self.widget.pack_start(self.sw)
		self.handlers = {
			'but_new': ('New',self.sig_new),
			'but_copy': ('Copy',self.sig_copy),
			'but_save': ('Save',self.sig_save),
			'but_save_as': ('Save As',self.sig_save_as),
			'but_import': ('Import',self.sig_import),
			'but_print_repeat': ('Repeat',self.sig_print_repeat),
			'but_remove': ('Remove',self.sig_remove),
			'but_search': ('Search',self.sig_search),
			'but_previous': ('Previous',self.sig_previous),
			'but_next': ('Next', self.sig_next),
			#'but_preference': ('Preferences', self.sig_preference),
			'but_goto_id': ('Go To ID...', self.sig_goto),
			'but_log': ('Access log', self.sig_logs),
			'but_print': ('Print', self.sig_print),
			'but_reload': (_('Reload'),self.sig_reload),
			'but_print_html': ('Print', self.sig_print_html),
			'but_action': ('Print', self.sig_action),
			'but_switch': ('Switch', self.sig_switch),
			'but_attach': ('Attach', self.sig_attach),
			'but_close': ('Close',self.sig_close)
		}
		if res_id:
			if isinstance(res_id, int):
				res_id = [res_id]
			self.screen.load(res_id)
		else:
			if len(view_type) and view_type[0]=='form':
				self.sig_new(autosave=False)

	def sig_goto(self, *args):
		if not self.modified_save():
			return
		glade2 = glade.XML(common.terp_path("terp.glade"),'dia_goto_id',gettext.textdomain())
		win = glade2.get_widget('dia_goto_id')
		widget = glade2.get_widget('goto_spinbutton')
		response = win.run()
		win.destroy()
		if response == gtk.RESPONSE_OK:
			self.screen.load( [int(widget.get_value())] )

	def destroy(self):
		oregistry.remove_receiver('misc-message', self._misc_message)
		self.screen.signal_unconnect(self)
		self.screen.destroy()
		del self.screen
		del self.glade
		del self.widget
		self.sw.destroy()
		del self.sw
		gc.collect()

	def ids_get(self):
		return self.screen.ids_get()

	def id_get(self):
		return self.screen.id_get()

	def _form_action_action(self, name, value):
		id = self.sig_save(sig_new=False)
		if id:
			id2 = value[2] or id
			obj = service.LocalService('action.main')
			action_id = int(value[0])
			obj.execute(action_id, {'model':value[1], 'id': id2, 'ids': [id2]})
			self.sig_reload()

	def _form_action_object(self, name, value):
		id = self.sig_save(sig_new=False, auto_continue=False)
		if id:
			id2 = value[2] or id
			rpc.session.rpc_exec_auth('/object', 'execute', value[1], value[0], [id2], rpc.session.context)
			self.sig_reload()

	def _form_action_workflow(self, name, value):
		id = self.sig_save(sig_new=False, auto_continue=False)
		if id:
			rpc.session.rpc_exec_auth('/object', 'exec_workflow', value[1], value[0], id)
			self.sig_reload()

	def sig_attach(self, widget=None):
		id = self.screen.id_get()
		if id:
			import win_attach
			win = win_attach.win_attach(self.model, id, parent=self.window)
			win.go()
		else:
			self.message_state(_('No resource selected !'))
		return True

	def sig_switch(self, widget=None, mode=None):
		#
		# Verifier pourquoi:
		#	1. Modif
		#	2. Switch & Cancel
		#	3. Re-Switch -> Question car modified
		#
		if not self.modified_save():
			return
		self.screen.switch_view()

	def _id_get(self):
		return self.screen.id_get()

	def sig_logs(self, widget=None):
		id = self._id_get()
		if not id:
			self.message_state(_('You have to select one resource!'))
			return False
		res = rpc.session.rpc_exec_auth('/object', 'execute', self.model, 'perm_read', [id])
		message = ''
		for line in res:
			todo = [
				('id', _('ID')),
				('create_uid', _('Creation User')),
				('create_date', _('Creation Date')),
				('write_uid', _('Latest Modification by')),
				('write_date', _('Latest Modification Date')),
				('uid', _('Owner')),
				('gid', _('Group Owner')),
				('level', _('Access Level'))
			]
			for (key,val) in todo:
				if line[key] and key in ('create_uid','write_uid','uid'):
					line[key] = line[key][1]
				message+=val+': '+str(line[key] or '/')+'\n'
		common.message(message)
		return True

	def sig_remove(self, widget=None):
		if common.sur(_('Are you sure to remove this record ?')):
			id = self.screen.remove(unlink=True)
			if not id:
				self.message_state(_('Resource not removed !'))
			else:
				self.message_state(_('Resource removed.'))

	def sig_import(self, widget=None):
		fields = []
		win = win_import.win_import(self.model, self.screen.fields, fields, parent=self.window)
		res = win.go()

	def sig_save_as(self, widget=None):
		fields = []
		win = win_export.win_export(self.model, self.screen.ids_get(), self.screen.fields, fields, parent=self.window)
		res = win.go()

	def sig_new(self, widget=None, autosave=True):
		if autosave:
			if not self.modified_save():
				return
		self.screen.new()
		self.message_state('')
	
	def sig_copy(self, *args):
		if not self.modified_save():
			return
		res_id = self._id_get()
		new_id = rpc.session.rpc_exec_auth('/object', 'execute', self.model, 'copy', res_id, {}, rpc.session.context)
		if new_id:
			self.screen.load([new_id])
			self.message_state(_('Working now on the duplicated document !'))

	def _form_save(self, auto_continue=True):
		pass

	def sig_save(self, widget=None, sig_new=True, auto_continue=True):
		id = self.screen.save_current()
		if id:
			self.message_state(_('Document saved !'))
		else:
			self.message_state(_('Invalid form !'))
		return bool(id)

	def sig_previous(self, widget=None):
		if not self.modified_save():
			return
		self.screen.display_prev()
		self.message_state('')

	def sig_next(self, widget=None):
		if not self.modified_save():
			return
		self.screen.display_next()
		self.message_state('')

	def sig_reload(self):
		if self.screen.current_view.view_type == 'form':
			self.screen.cancel_current()
			self.screen.display()
		else:
			id = self.screen.id_get()
			ids = self.screen.ids_get()
			self.screen.clear()
			self.screen.load(ids)
			for model in self.screen.models:
				if model.id == id:
					self.screen.current_model = model
					self.screen.display()
					break
		self.message_state('')

	def sig_action(self, keyword='client_action_multi', previous=False, report_type='pdf', adds={}):
		ids = self.screen.ids_get()
		if self.screen.current_model:
			id = self.screen.current_model.id
		else:
			id = False
		if self.screen.current_view.view_type == 'form':
			id = self.screen.save_current()
			if not id:
				return False
			ids = [id]
		if len(ids):
			obj = service.LocalService('action.main')
			if previous and self.previous_action:
				obj._exec_action(self.previous_action[1], {'model':self.screen.resource, 'id': id or False, 'ids':ids, 'report_type': report_type})
			else:
				res = obj.exec_keyword(keyword, {'model':self.screen.resource, 'id': id or False, 'ids':ids, 'report_type': report_type}, adds=adds)
				if res:
					self.previous_action = res
			self.sig_reload()
		else:
			self.message_state(_('No record selected!'))

	def sig_print_repeat(self):
		self.sig_action('client_print_multi', True)

	def sig_print_html(self):
		self.sig_action('client_print_multi', report_type='html')

	def sig_print(self):
		self.sig_action('client_print_multi', adds={'Print Screen': {'report_name':'printscreen.list', 'name':'Print Screen', 'type':'ir.actions.report.xml'}})

	def sig_search(self, widget=None):
		if not self.modified_save():
			return
		dom = self.domain
		win = win_search.win_search(self.model, domain=self.domain, context=self.context, parent=self.window)
		res = win.go()
		if res:
			self.screen.clear()
			self.screen.load(res)

	def message_state(self, message, context='message'):
		sb = self.glade.get_widget('stat_state')
		cid = sb.get_context_id(context)
		sb.push(cid, message)

	def _record_message(self, screen, signal_data):
		if not signal_data[1]:
			msg = _('No record selected')
		else:
			name = '_'
			if signal_data[0]>=0:
				name = str(signal_data[0]+1)
			name2 = _('New document')
			if signal_data[2]:
				name2 = _('Editing document (id: ')+str(signal_data[2])+')'
			msg = _('Record: ')+name+' / '+str(signal_data[1])+' - '+name2
		sb = self.glade.get_widget('stat_form')
		cid = sb.get_context_id('message')
		sb.push(cid, msg)

	def _misc_message(self, obj, message):
		self.message_state(message)

	def sig_preference(self, widget=None):
		actions = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.values', 'get', 'meta', False, [(self.model,False)], True, rpc.session.context, True)
		id = self.screen.id_get()
		if id and len(actions):
			win = win_preference.win_preference(self.model, id, actions)
			win.run()
		elif id:
			self.message_state(_('No preference available for this resource !'))
		else:
			self.message_state(_('No resource selected !'))

	def modified_save(self, reload=True):
		if self.screen.is_modified():
			value = common.sur_3b(_('This record has been modified\ndo you want to save it ?'))
			if value == 'ok':
				return self.sig_save()
			elif value == 'ko':
				if reload:
					self.sig_reload()
				return True
			else:
				return False
		return True

	def sig_close(self, urgent=False):
		return self.modified_save(reload=False)
