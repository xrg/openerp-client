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

import gobject
import gtk
from gtk import glade
import copy

import gettext

import interface
import wid_common
import common

import widget
from widget.screen import Screen

from modules.gui.window.win_search import win_search
import rpc

import service


class dialog(object):
	def __init__(self, model, id=None, attrs={}):
		self.win_gl = glade.XML(common.terp_path("terp.glade"), "dia_form_win_many2one", gettext.textdomain())
		self.dia = self.win_gl.get_widget('dia_form_win_many2one')
		if ('string' in attrs) and attrs['string']:
			self.dia.set_title(self.dia.get_title() + ' - ' + attrs['string'])
		self.sw = self.win_gl.get_widget('many2one_vp')

		self.screen = Screen(model)
		if id:
			self.screen.load([id])
		else:
			self.screen.new()
		self.screen.display()
		self.sw.add(self.screen.widget)
		#self.sw.show_all()

	def run(self, datas={}):
		while True:
			res = self.dia.run()
			if res==gtk.RESPONSE_OK:
				if self.screen.current_model.validate():
					self.screen.save_current()
					return (True, self.screen.current_model.name_get())
				else:
					self.screen.display()
			else:
				break
		return (False, False)

	def destroy(self):
		self.dia.destroy()

class many2one(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		self._readonly = False
		interface.widget_interface.__init__(self, window, parent, model, attrs)
		self.win_gl = glade.XML(common.terp_path("terp.glade"),"widget_reference", gettext.textdomain())
		self.win_gl.signal_connect('on_reference_new_button_press', self.sig_new )
		self.win_gl.signal_connect('on_reference_edit_button_press', self.sig_edit )
		self.widget = self.win_gl.get_widget('widget_reference')
		self.model_type = attrs['relation']
		
		self._menu_loaded = False
		self._menu_entries.append((None, None, None))
		self._menu_entries.append((_('Action'), lambda x: self.click_and_action('client_action_multi'),0))
		self._menu_entries.append((_('Report'), lambda x: self.click_and_action('client_print_multi'),0))

		self.parent = parent
		#self.widget.set_property('can-focus', True)
		#self.widget.set_property('can-default', True)

		#self.widget.set_property('sensitive', False)
		self.widget.set_property('sensitive', True)

		self.win_gl.get_widget('but_many2one_new').set_property('can-focus', False)
		self.win_gl.get_widget('but_many2one_open').set_property('can-focus', False)

		self.wid_text = self.win_gl.get_widget('ent_reference')
		self.ok = True
		self.wid_text.connect_after('changed', self.sig_changed)
		self.wid_text.connect('key_press_event', self.sig_key_press)
		self.wid_text.connect_after('activate', self.sig_activate)
		self.wid_text.connect('button_press_event', self._menu_open)
		self.image_search = self.win_gl.get_widget('but_m2o_image')

		if attrs.get('completion',False):
			ids = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['relation'], 'name_search', '', [], 'ilike', {})
			if ids:
				self.load_completion(ids,attrs)

	def load_completion(self,ids,attrs):
		self.completion = gtk.EntryCompletion()
		self.completion.set_match_func(self.match_func, None)
		self.completion.connect("match-selected", self.on_completion_match)
		self.wid_text.set_completion(self.completion)
		self.liststore = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
		self.completion.set_model(self.liststore)
		self.completion.set_text_column(0)
		for i,word in enumerate(ids):
			if word[1][0] == '[':
				i = word[1].find(']')
				s = word[1][1:i]
				s2 = word[1][i+2:]
				self.liststore.append([("%s %s" % (s,s2)),s2])
			else:
				self.liststore.append([word[1],word[1]])

	def match_func(self, completion, key_string, iter, data):
		model = self.completion.get_model()
		modelstr = model[iter][0].lower()
		return modelstr.startswith(key_string)
		 
	def on_completion_match(self, completion, model, iter):
		current_text = self.wid_text.get_text()
		current_text = model[iter][1]
		name = model[iter][1]
		domain = self._view.modelfield.domain_get()
		context = self._view.modelfield.context_get()
		ids = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['relation'], 'name_search', name, domain, 'ilike', context)
		if len(ids)==1:
			self._view.modelfield.set_client(self._view.model, ids[0])
			self.display(self._view.model, self._view.modelfield)
			self.ok = True
			# return True
		else:
			win = win_search(self.attrs['relation'], sel_multi=False, ids=map(lambda x: x[0], ids), context=context, domain=domain)
			ids = win.go()
			if ids:
				name = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['relation'], 'name_get', [ids[0]], rpc.session.context)[0]
				self._view.modelfield.set_client(self._view.model, name)
		return True



	def _readonly_set(self, value):
		self._readonly = value
		self.wid_text.set_editable(not value)
		self.wid_text.set_sensitive(not value)
		self.win_gl.get_widget('but_many2one_new').set_sensitive(not value)

	def _color_widget(self):
		return self.wid_text

	def _menu_sig_pref(self, obj):
		self._menu_sig_default_set()

	def _menu_sig_default(self, obj):
		res = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['model'], 'default_get', [self.attrs['name']])
		self.value = res.get(self.attrs['name'], False)

	def sig_activate(self, *args):
		self.ok = False
		value = self._view.modelfield.get(self._view.model)

		if value:
			dia = dialog(self.attrs['relation'], self._view.modelfield.get(self._view.model), attrs=self.attrs)
			ok, value = dia.run()
			if ok:
				self._view.modelfield.set_client(self._view.model, value)
				self.value = value
			dia.destroy()
		else:
			if not self._readonly:
				domain = self._view.modelfield.domain_get(self._view.model)
				context = self._view.modelfield.context_get(self._view.model)

				ids = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['relation'], 'name_search', self.wid_text.get_text(), domain, 'ilike', context)
				if len(ids)==1:
					self._view.modelfield.set_client(self._view.model, ids[0])
					self.display(self._view.model, self._view.modelfield)
					self.ok = True
					return True

				win = win_search(self.attrs['relation'], sel_multi=False, ids=map(lambda x: x[0], ids), context=context, domain=domain)
				ids = win.go()
				if ids:
					name = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['relation'], 'name_get', [ids[0]], rpc.session.context)[0]
					self._view.modelfield.set_client(self._view.model, name)
		self.display(self._view.model, self._view.modelfield)
		self.ok=True

	def sig_new(self, *args):
		dia = dialog(self.attrs['relation'], attrs=self.attrs)
		ok, value = dia.run()
		if ok:
			self._view.modelfield.set_client(self._view.model, value)
			self.display(self._view.model, self._view.modelfield)
		dia.destroy()
	sig_edit = sig_activate

	def sig_key_press(self, widget, event, *args):
		if event.keyval==gtk.keysyms.F1:
			self.sig_new()
		elif event.keyval==gtk.keysyms.F2:
			self.sig_activate()
		return False

	def sig_changed(self, *args):
		if self.ok:
			if self._view.modelfield.get(self._view.model):
				self._view.modelfield.set_client(self._view.model, False)
				self.display(self._view.model, self._view.modelfield)
		return False

	#
	# No update of the model, the model is updated in real time !
	#
	def set_value(self, model, model_field):
		pass

	def display(self, model, model_field):
		if not model_field:
			self.ok = False
			self.wid_text.set_text('')
			return False
		super(many2one, self).display(model, model_field)
		self.ok=False
		res = model_field.get_client(model)
		self.wid_text.set_text(res or '')
		if res:
			self.image_search.set_from_stock('gtk-open',gtk.ICON_SIZE_BUTTON)
		else:
			self.image_search.set_from_stock('gtk-find',gtk.ICON_SIZE_BUTTON)
		self.ok=True

	def _menu_open(self, obj, event):
		if event.button == 3:
			value = self._view.modelfield.get(self._view.model)
			if not self._menu_loaded:
				fields_id = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.model.fields', 'search',[('relation','=',self.model_type),('ttype','=','many2one'),('relate','=',True)])
				fields = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.model.fields', 'read', fields_id, ['name','model_id'], rpc.session.context)
				models_id = [x['model_id'][0] for x in fields if x['model_id']]
				fields = dict(map(lambda x: (x['model_id'][0], x['name']), fields))
				models = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.model', 'read', models_id, ['name','model'], rpc.session.context)
				self._menu_entries.append((None, None, None))
				for model in models:
					field = fields[model['id']]
					model_name = model['model']
					f = lambda model_name,field: lambda x: self.click_and_relate(model_name,field)
					self._menu_entries.append(('... '+model['name'], f(model_name,field), 0))
			self._menu_loaded = True

			menu = gtk.Menu()
			for stock_id,callback,sensitivity in self._menu_entries:
				if stock_id:
					item = gtk.ImageMenuItem(stock_id)
					if callback:
						item.connect("activate",callback)
					item.set_sensitive(bool(sensitivity or value))
				else:
					item=gtk.SeparatorMenuItem()
				item.show()
				menu.append(item)
			menu.popup(None,None,None,event.button,event.time)
			return True
		return False

	#
	# Open a view with ids: [(field,'=',value)]
	#
	def click_and_relate(self, model, field):
		value = self._view.modelfield.get(self._view.model)
		ids = rpc.session.rpc_exec_auth('/object', 'execute', model, 'search',[(field,'=',value)])
		obj = service.LocalService('gui.window')
		#view_ids = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.ui.view', 'search', [('model','=',model),('type','=','form')])
		obj.create(False, model, ids, [(field,'=',value)], 'form', None, mode='tree,form')
		return True

	def click_and_action(self, type):
		id = self._view.modelfield.get(self._view.model)
		obj = service.LocalService('action.main')
		res = obj.exec_keyword(type, {'model':self.model_type, 'id': id or False, 'ids':[id], 'report_type': 'pdf'})
		return True

