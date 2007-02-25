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

import gtk
from gtk import glade

import interface

class textbox(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		interface.widget_interface.__init__(self, window, parent, model, attrs)
		self.tv = gtk.TextView()
		self.tv.set_wrap_mode(gtk.WRAP_WORD)
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
		sw.set_shadow_type(gtk.SHADOW_NONE)
		sw.set_size_request(-1, 80)
		sw.add(self.tv)
		self.widget=sw
		self.tv.connect('button_press_event', self._menu_open)
		self.tv.set_accepts_tab(False)
#		if self.attrs['readonly']:
#			self.tv.set_editable(False)
#			self.widget.set_sensitive(False)
		self.tv.connect('focus-out-event', lambda x,y: self._focus_out())
		sw.show_all()

	def _readonly_set(self, value):
		interface.widget_interface._readonly_set(self, value)
		self.tv.set_editable(not value)
		self.tv.set_sensitive(not value)

	def _color_widget(self):
		return self.tv

	def set_value(self, model, model_field):
		buffer = self.tv.get_buffer()
		iter_start = buffer.get_start_iter()
		iter_end = buffer.get_end_iter()
		current_text = buffer.get_text(iter_start,iter_end,False)
		model_field.set_client(model, current_text or False)

	def display(self, model, model_field):
		super(textbox, self).display(model, model_field)
		value = model_field and model_field.get(model)
		if not value:
			value=''
		buffer = self.tv.get_buffer()
		buffer.delete(buffer.get_start_iter(), buffer.get_end_iter())
		iter_start = buffer.get_start_iter()
		buffer.insert(iter_start, value)
