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

from widget import ViewWidget

import gtk
from gtk import glade

import common
import rpc
import service

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

		if toolbar:
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

					def _relate(button, data):
						id = self.screen.current_model and self.screen.current_model.id
						if not (id):
							common.message(_('You must select a record to use the relate button !'))
						model,field = data
						ids = rpc.session.rpc_exec_auth('/object', 'execute', model, 'search',[(field,'=',id)])
						obj = service.LocalService('gui.window')
						return obj.create(False, model, ids, [(field,'=',id)], 'form', None, mode='tree,form')
					def _action(button, action):
						self.screen.save_current()
						id = self.screen.current_model and self.screen.current_model.id
						if not (id):
							common.message(_('You must save this record to use the relate button !'))
							return False
						data = {
							'id': id,
							'ids': [id]
						}
						self.screen.display()
						obj = service.LocalService('action.main')
						value = obj._exec_action(action, data)
						self.screen.reload()
						return value

					if icontype in ('relate',):
						tbutton.connect('clicked', _relate, (tool['model_id'][1], tool['name']))
					elif icontype in ('action','print'):
						tbutton.connect('clicked', _action, tool)

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

	def reset(self):
		for wid_name, widget in self.widgets.items():
			widget.reset()

	def signal_record_changed(self, *args):
		pass

	def display(self):
		model = self.screen.current_model
		if model and ('state' in model.fields):
			state = model['state'].get()
		else:
			state = 'draft'
		for widget in self.widgets.values():
			widget.display(model, state)
		for button in self.buttons:
			button.state_set(state)
		return True
