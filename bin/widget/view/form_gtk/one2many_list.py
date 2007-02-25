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

import gettext

import common
import wid_common

import interface
from widget.screen import Screen

class dialog(object):
	def __init__(self, model_name, parent, model=None, attrs={}):
		self.win_gl = glade.XML(common.terp_path("terp.glade"),"dia_form_win_many2one",gettext.textdomain())
		self.dia = self.win_gl.get_widget('dia_form_win_many2one')
		if ('string' in attrs) and attrs['string']:
			self.dia.set_title(self.dia.get_title() + ' - ' + attrs['string'])
		self.sw = self.win_gl.get_widget('many2one_vp')
		self.screen = Screen(model_name, view_type=[], parent=parent)
		if not model:
			model = self.screen.new()
		self.screen.models.model_add(model)
		self.screen.current_model = model
		if ('views' in attrs) and ('form' in attrs['views']):
			arch = attrs['views']['form']['arch']
			fields = attrs['views']['form']['fields']
			self.screen.add_view(arch, fields, display=True)
		else:
			self.screen.add_view_id(False, 'form', display=True)
		self.sw.add(self.screen.widget)
		self.screen.display()
		x,y = self.screen.screen_container.size_get()
		self.sw.set_size_request(x,y+30)
		#self.sw.show_all()

	def new(self):
		model = self.screen.new()
		self.screen.models.model_add(model)
		self.screen.current_model = model
		return True

	def run(self, datas={}):
		end = False
		while not end:
			res = self.dia.run()
			end = (res != gtk.RESPONSE_OK) or self.screen.current_model.validate()
			if not end:
				self.screen.display()

		if res==gtk.RESPONSE_OK:
			self.screen.current_view.set_value()
			model = self.screen.current_model
			return (True, model)
		return (False, False)

	def destroy(self):
		self.screen.signal_unconnect(self)
		self.dia.destroy()
		self.screen.destroy()


class one2many_list(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		interface.widget_interface.__init__(self, window, parent, model, attrs)

		self.win_gl = glade.XML(common.terp_path("terp.glade"), "widget_one2many_list", gettext.textdomain())

		self.win_gl.signal_connect('on_o2m_but_new_button_press_event', self._sig_new)
		self.win_gl.signal_connect('on_o2m_but_open_button_press_event', self._sig_edit)
		self.win_gl.signal_connect('on_o2m_but_delete_button_press_event', self._sig_remove )

		self.win_gl.signal_connect('on_o2m_but_next_button_press_event', self._sig_next )
		self.win_gl.signal_connect('on_o2m_but_previous_button_press_event', self._sig_previous )

		self.win_gl.signal_connect('on_o2ml_but_refresh_button_press_event',
								   self._sig_refresh )
		self.win_gl.signal_connect('on_o2ml_but_sequence_clicked',
								   self._sig_sequence )
		self.win_gl.signal_connect('on_o2ml_but_switchview_clicked',
								   self.switch_view)

		self.screen = Screen(attrs['relation'], view_type=attrs.get('mode','tree,form').split(','), parent=parent, views_preload=attrs.get('views', {}), tree_saves=False, create_new=True, row_activate=self._on_activate)
		self.screen.signal_connect(self, 'record-message', self._sig_label)

		self.widget = self.win_gl.get_widget('widget_one2many_list')
		self.sw = self.win_gl.get_widget('o2ml_sw')
		self.sw.add_with_viewport(self.screen.widget)
		
		title = self.win_gl.get_widget('o2m_menuitem_titre')
		title.get_child().set_text(self.screen.current_view.title)

		self.win_gl.signal_connect('on_set_default_activate', lambda *x: self._menu_sig_default_set() )
		self.win_gl.signal_connect('on_set_to_default_activate', lambda *x:self._menu_sig_default_get() )

	def destroy(self):
		self.screen.destroy()
		del self.win_gl

	def _on_activate(self, screen, *args):
		self._sig_edit()

	def click_and_action(self, type):
		pos = self.tree_view.pos_get()
		if pos!=None:
			val = self._value[pos]
			id = val.get('id', False)
			obj = service.LocalService('action.main')
			res = obj.exec_keyword(type, {'model':self.model, 'id': id or False, 'ids':[id], 'report_type': 'pdf'})
			return True
		else:
			common.message(_('You have to select a resource !'))
			return False

	def switch_view(self, btn, arg):
		self.screen.switch_view()

	def _readonly_set(self, value):
		self.win_gl.get_widget('o2m_but_new').set_sensitive(not value)
		self.win_gl.get_widget('o2m_but_delete').set_sensitive(not value)
		self.win_gl.get_widget('o2m_but_open').set_sensitive(not value)

	def _sig_new(self, *args):
		_, event = args
		if event.type == gtk.gdk.BUTTON_PRESS :
			if (self.screen.current_view.view_type=='form') or self.screen.editable_get():
				self.screen.new()
				self.screen.current_view.widget.set_sensitive(True)
			else:
				parent = self._view.model
				ok = 1
				dia = dialog(self.attrs['relation'], parent=parent, attrs=self.attrs)
				while ok:
					ok, value = dia.run()
					if ok:
						self.screen.models.model_add(value)
						self.screen.display()
						dia.new()
				dia.destroy()

	def _sig_edit(self, *args):
		dia = dialog(self.attrs['relation'], parent=self._view.model,  model=self.screen.current_model, attrs=self.attrs) 
		ok, value = dia.run()
		dia.destroy()
#		self.screen.display()

	def _sig_next(self, *args):
		_, event = args
		if event.type == gtk.gdk.BUTTON_PRESS:
			self.screen.display_next()

	def _sig_previous(self, *args):
		_, event = args
		if event.type == gtk.gdk.BUTTON_PRESS:
			self.screen.display_prev()

	def _sig_remove(self, *args):
		_, event = args
		if event.type == gtk.gdk.BUTTON_PRESS:
			self.screen.remove()
			if not self.screen.models.models:
				self.screen.current_view.widget.set_sensitive(False)

	def _sig_label(self, screen, signal_data):
		name = '_'
		if signal_data[0] >= 0:
			name = str(signal_data[0] + 1)
		line = '(%s/%s)' % (name, signal_data[1])
		self.win_gl.get_widget('one2many_label').set_text(line)

	def _sig_refresh(self, *args):
		pass

	def _sig_sequence(self, *args):
		pass

	def display(self, model, model_field):
		if not model_field:
			self.screen.current_model = None
			self.screen.display()
			return False
		super(one2many_list, self).display(model, model_field)
		new_models = model_field.get_client(model)
		if self.screen.models != new_models:
			self.screen.models_set(new_models)
			if (self.screen.current_view.view_type=='tree') and self.screen.editable_get():
				self.screen.current_model = None
			self.screen.display()
		else:
			self.screen.display()
		return True

	def set_value(self, model, model_field):
		self.screen.current_view.set_value()
		return True
