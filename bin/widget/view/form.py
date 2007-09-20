##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import gtk
from gtk import glade

import common
import rpc
import service
import options
from form_gtk.action import action

class ViewWidget(object):
	def __init__(self, parent, widget, widget_name):
		self.view_form = parent
		self.widget = widget
		self.widget._view = self
		self.widget_name = widget_name

	def display(self, model, state='draft'):
		if not model:
			self.widget.display(model, False)
			return False
		modelfield = model.mgroup.mfields.get(self.widget_name, False)
		if modelfield:
			modelfield.state_set(model, state)
			self.widget.display(model, modelfield)
		elif isinstance(self.widget, action):
			self.widget.display(model, False)

	def reset(self, model):
		modelfield = False
		if model:
			modelfield = model.mgroup.mfields.get(self.widget_name, False)
			if modelfield and 'valid' in modelfield.get_state_attrs(model):
				modelfield.get_state_attrs(model)['valid'] = True
		self.display(model, modelfield)

	def set_value(self, model):
		if self.widget_name in model.mgroup.mfields:
			self.widget.set_value(model, model.mgroup.mfields[self.widget_name])

	def _get_model(self):
		return self.view_form.screen.current_model

	model = property(_get_model)

	def _get_modelfield(self):
		if self.model:
			return self.model.mgroup.mfields[self.widget_name]

	modelfield = property(_get_modelfield)

class ViewForm(object):
	def __init__(self, screen, widget, children, buttons=[], toolbar=None):
		self.view_type = 'form'
		self.screen = screen
		self.widget = widget
		self.model_add_new = False
		self.buttons = buttons
		for button in self.buttons:
			button.form = self

		self.widgets = dict([(name, ViewWidget(self, widget, name))
							 for name, widget in children.items()])

		if toolbar and not options.options['client.modepda']:
			hb = gtk.HBox()
			hb.pack_start(self.widget)

			#tb = gtk.Toolbar()
			#tb.set_orientation(gtk.ORIENTATION_VERTICAL)
			#tb.set_style(gtk.TOOLBAR_BOTH_HORIZ)
			#tb.set_icon_size(gtk.ICON_SIZE_MENU)
			tb = gtk.VBox()
			hb.pack_start(tb, False, False)
			self.widget = hb

			sep = False
			for icontype in ('print', 'action', 'relate'):
				if icontype in ('action','relate') and sep:
					#tb.insert(gtk.SeparatorToolItem(), -1)
					tb.pack_start(gtk.HSeparator(), False, False, 2)
					sep = False
				for tool in toolbar[icontype]:
					iconstock = {
						'print': gtk.STOCK_PRINT,
						'action': gtk.STOCK_EXECUTE,
						'relate': gtk.STOCK_JUMP_TO,
					}.get(icontype, gtk.STOCK_ABOUT)



					icon = gtk.Image() 
					icon.set_from_stock(iconstock, gtk.ICON_SIZE_BUTTON)
					hb = gtk.HBox(False, 5)
					hb.pack_start(icon, False, False)
					hb.pack_start(gtk.Label(tool['string']), False, False)

					tbutton = gtk.Button()
					tbutton.add(hb)
					tbutton.set_relief(gtk.RELIEF_NONE)
					tb.pack_start(tbutton, False, False, 2)

					#tbutton = gtk.ToolButton()
					#tbutton.set_label_widget(hb) #tool['string'])
					#tbutton.set_stock_id(iconstock)
					#tb.insert(tbutton,-1)

					def _action(button, action, type):
						data={}
						context={}
						act=action.copy()
						if type in ('print', 'action'):
							self.screen.save_current()
							id = self.screen.current_model and self.screen.current_model.id
							if not (id):
								common.message(_('You must save this record to use the relate button !'))
								return False
							self.screen.display()
							data = {
								'model': self.screen.name,
								'id': id,
								'ids': [id],
								'report_type': 'pdf',
							}
						if type == 'relate':
							id = self.screen.current_model and self.screen.current_model.id
							if not (id):
								common.message(_('You must select a record to use the relate button !'))
								return False
							act['domain'] = self.screen.current_model.expr_eval(act['domain'], check_load=False)
							act['context'] = str(self.screen.current_model.expr_eval(act['context'], check_load=False))
						obj = service.LocalService('action.main')
						value = obj._exec_action(act, data, context)
						if type in ('print', 'action'):
							self.screen.reload()
						return value

					def _translate_label(self, event, tool):
						if event.button != 3:
							return False
						def callback(self, tool):
							lang_ids = rpc.session.rpc_exec_auth('/object', 'execute', 'res.lang', 'search', [('translatable', '=', '1')])
							langs = rpc.session.rpc_exec_auth('/object', 'execute', 'res.lang', 'read', lang_ids, ['code', 'name'])

							win = gtk.Dialog(_('Add Translation'))
							win.vbox.set_spacing(5)
							vbox = gtk.VBox(spacing=5)

							entries_list = []
							for lang in langs:
								code = lang['code']
								val = rpc.session.rpc_exec_auth('/object', 'execute', tool['type'], 'read', [tool['id']], ['name'], {'lang': code})
								val = val[0]

								label = gtk.Label(lang['name'])
								entry = gtk.Entry()
								entry.set_text(val['name'])
								entries_list.append((code, entry))
								hbox = gtk.HBox(homogeneous=True)
								hbox.pack_start(label, expand=False, fill=False)
								hbox.pack_start(entry, expand=True, fill=True)
								vbox.pack_start(hbox, expand=False, fill=True)
							vp = gtk.Viewport()
							vp.set_shadow_type(gtk.SHADOW_NONE)
							vp.add(vbox)
							sv = gtk.ScrolledWindow()
							sv.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
							sv.set_shadow_type(gtk.SHADOW_NONE)
							sv.add(vp)
							win.vbox.add(sv)
							win.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
							win.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
							win.resize(400,200)
							win.show_all()
							ok = False
							while not ok:
								res = win.run()
								ok = True
								if res == gtk.RESPONSE_OK:
									to_save = map(lambda x: (x[0], x[1].get_text()), entries_list)
									while to_save:
										code, val = to_save.pop()
										rpc.session.rpc_exec_auth('/object', 'execute', tool['type'], 'write', [tool['id']], {'name': val}, {'lang': code})
								if res == gtk.RESPONSE_CANCEL:
									win.destroy()
									return
							win.destroy()
							return True
						menu = gtk.Menu()
						item = gtk.ImageMenuItem(_('Translate label'))
						item.connect("activate", callback, tool)
						item.set_sensitive(1)
						item.show()
						menu.append(item)
						menu.popup(None,None,None,event.button,event.time)
						return True

					tbutton.connect('clicked', _action, tool, icontype)

					tbutton.connect('button_press_event', _translate_label, tool)

					sep = True


	def __getitem__(self, name):
		return self.widgets[name]
	
	def destroy(self):
		self.widget.destroy()
		for widget in self.widgets.keys():
			self.widgets[widget].widget.destroy()
			del self.widgets[widget]
		del self.widget
		del self.widgets
		del self.screen
		del self.buttons
	
	def cancel(self):
		pass

	def set_value(self):
		model = self.screen.current_model
		if model:
			for widget in self.widgets.values():
				widget.set_value(model)

	def sel_ids_get(self):
		if self.screen.current_model:
			return [self.screen.current_model.id]
		return []

	def sel_models_get(self):
		if self.screen.current_model:
			return [self.screen.current_model]
		return []

	def reset(self):
		model = self.screen.current_model
		for wid_name, widget in self.widgets.items():
			widget.reset(model)

	def signal_record_changed(self, *args):
		pass

	def display(self):
		model = self.screen.current_model
		if model and ('state' in model.mgroup.fields):
			state = model['state'].get(model)
		else:
			state = 'draft'
		for widget in self.widgets.values():
			widget.display(model, state)
		for button in self.buttons:
			button.state_set(state)
		return True

	def set_cursor(self, new=False):
		pass
