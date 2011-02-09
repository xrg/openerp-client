# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import gtk
from gtk import glade
import wid_int
import calendar
from calendar import calendar,datetime
from spinbutton import spinbutton
from spinint import spinint
from selection import selection
import char
import checkbox
from reference import reference
import common
import gettext

class custom_filter(wid_int.wid_int):
	def __init__(self, name, parent, attrs={}, call=None):
		wid_int.wid_int.__init__(self, name, parent, attrs)

		self.field_selection = {}
		self.op_selection = {}

		self.widget = gtk.HBox()

		self.combo_fields =  gtk.combo_box_new_text()
		self.combo_fields.connect('changed', self.on_fields_combo_changed)

		self.combo_op = gtk.combo_box_new_text()
		self.combo_op.connect('changed', self.on_operator_combo_changed)

		self.condition_next = gtk.combo_box_new_text()
		self.condition_next.append_text(_('AND'))
		self.condition_next.append_text(_('OR'))
		self.condition_next.set_active(0)
		self.condition_next.hide()

		self.remove_filter = gtk.Button()
		img = gtk.Image()
		img.set_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_BUTTON)
		self.remove_filter.add(img)
		self.remove_filter.set_relief(gtk.RELIEF_NONE)
		self.remove_filter.connect('clicked', call, self)

		self.right_text = gtk.Entry()

		self.widget.pack_start(self.combo_fields)
		self.widget.pack_start(self.combo_op)
		self.widget.pack_start(self.right_text)
		self.widget.pack_start(self.condition_next)
		self.widget.pack_start(self.remove_filter)
		self.widget.show_all()

		fields = attrs.get('fields',None)
		for item in fields:
			self.field_selection[item[1]] = (item[0], item[2], item[3])
			self.combo_fields.append_text(item[1])

		self.combo_fields.set_active(0)

	def on_operator_combo_changed(self, combo):
		self.widget_obj.selected_oper_text = self.combo_op.get_active_text()
		self.widget_obj.set_visibility()
		return True

	def on_fields_combo_changed(self, combo):
		field_string = self.combo_fields.get_active_text()
		field_dbname, type, default_val = self.field_selection[field_string]
		if self.right_text:
			self.widget.remove(self.right_text)
		self.widget_obj = widgets_type[type](field_string, self.parent, default_val or {})
		self.right_text = self.widget_obj.widget
		self.op_selection = {}
		self.combo_op.get_model().clear()
		for operator in self.widget_obj.operators:
			self.op_selection[operator[1]] = operator[0]
			self.combo_op.append_text(operator[1])
		self.combo_op.set_active(0)
		self.widget.pack_start(self.right_text)
		self.widget.reorder_child(self.right_text, 2)
		self.widget.show_all()
		self.condition_next.hide()
		return True

	def _value_get(self):
		field_left = self.field_selection[self.combo_fields.get_active_text()][0]
		self.widget_obj.selected_oper_text = self.combo_op.get_active_text()
		self.widget_obj.selected_oper = self.op_selection[self.widget_obj.selected_oper_text]
		operator, right_text = self.widget_obj._value_get()
		condition = self.condition_next.get_active() == 0 and '&' or '|'
		domain = [condition, (field_left, operator, right_text)]
		return {'domain':domain}

	def sig_exec(self, widget):
		pass

	def clear(self):
		pass

	def _value_set(self, value):
		pass

	def remove_custom_widget(self, button):
		button.parent.destroy()
		return True

	def sig_activate(self, fct):
		self.right_text.connect_after('activate', fct)

	value = property(_value_get, _value_set, None,
	 _('The content of the widget or ValueError if not valid'))

class char(char.char):
	def __init__(self, name, parent, attrs={}, screen=None):
		super(char,self).__init__(name,parent,attrs, screen)
		self.operators = (['=', _('is')],
						  ['<>',_('is not')],
						  ['=', _('is Empty')],
						  ['<>',_('is not Empty')],
						  ['ilike', _('contains')],
						  ['not ilike', _('doesn\'t contain')])
		self.selected_oper = False
		self.selected_oper_text = False

	def _value_get(self):
		if self.selected_oper_text in ['is Empty', 'is not Empty']:
			text = False
		else:
			text = self.widget.get_text()
		return (self.selected_oper, text)

	def set_visibility(self):
		if self.selected_oper_text in ['is Empty', 'is not Empty']:
			self.widget.hide()
		else:
			self.widget.show()

	value = property(_value_get, _value_set, None, _('The content of the widget or ValueError if not valid'))

class checkbox(wid_int.wid_int):
	def __init__(self, name, parent, attrs={}, screen=None):
		wid_int.wid_int.__init__(self, name, parent, attrs, screen)
		self.widget = gtk.CheckButton()
		self.widget.set_active(False)
		self.operators = (['=', _('Equals')],)
		self.selected_oper = False
		self.selected_oper_text = False

	def _value_get(self):
		return (self.selected_oper, int(self.widget.get_active()))

	value = property(_value_get, _value_set, None, _('The content of the widget or ValueError if not valid'))
#
class calendar(calendar):
	def __init__(self, name, parent, attrs={}, screen=None):
		super(calendar,self).__init__(name, parent, attrs, screen)
		self.operators =  (['=', _('is')],
						  ['<>',_('is not')],
						  ['', _('between')],
						  ['<>',_('is not Empty')],
						  ['ilike', _(' exclude range')])

class datetime(datetime):
	def __init__(self, name, parent, attrs={}, screen=None):
		super(datetime,self).__init__(name, parent, attrs, screen)
		self.operators =  (['=', _('is')],
						  ['<>',_('is not')],
						  ['*', _('between')],
						  ['<>',_('is not Empty')],
						  ['**', _('exclude range')])

class reference(reference):
	def __init__(self, name, parent, attrs={},screen=None):
		new_attrs = {}
		if attrs:
			new_attrs.update({'selection':attrs})
		super(reference,self).__init__(name, parent, new_attrs, screen)
		self.operators =  (['=', _('is')],
						  ['<>',_('is not')])

class selection(selection):
	def __init__(self, name, parent, attrs={}, model=None, screen=None):
		new_attrs = {}
		if attrs:
			new_attrs.update({'selection':attrs})
		super(selection,self).__init__(name, parent, new_attrs, screen)
		self.operators =  (['=', _('is')],
						  ['<>',_('is not')])

#
class spinbutton(spinbutton):
	def __init__(self, name, parent, attrs={},screen=None):
		super(spinbutton,self).__init__(name, parent, attrs, screen)
		self.operators = (['=', _('is equal to')],
						  ['<>',_('is not equal to')],
						  ['>',_('greater than')],
						  ['<',_('less than')],
						  ['>=',_('greater than equal to')],
						  ['<=',_('less than equal to')],
						  ['*',_('between')],
						  ['**',_('exclude range')])

class spinint(spinint):
	def __init__(self, name, parent, attrs={},screen=None):
		super(spinint,self).__init__(name, parent, attrs, screen)
		self.operators = (['=', _('is equal to')],
						  ['<>',_('is not equal to')],
						  ['>',_('greater than')],
						  ['<',_('less than')],
						  ['>=',_('greater than equal to')],
						  ['<=',_('less than equal to')],
						  ['*',_('between')],
						  ['**',_('exclude range')])

widgets_type = {
	'date': calendar,
	'datetime': datetime,
	'float': spinbutton,
	'integer': spinint,
	'selection': selection,
	'char': char,
	'boolean': checkbox,
	'text': char,
	'many2one':char,
	'one2many':char,
	'many2many':char,
	'reference':reference
	}