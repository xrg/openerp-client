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

import gettext
import gtk
from gtk import glade

import common
import interface
import tools

class url(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		self.win_gl = glade.XML(common.terp_path("terp.glade"), "widget_url", 
								gettext.textdomain())
		self.widget = self.win_gl.get_widget('widget_url')

		self.entry = self.win_gl.get_widget('entry_url')
		self.entry.connect('activate', self.sig_activate)
		self.entry.connect('focus-in-event', lambda x,y: self._focus_in())
		self.entry.connect('focus-out-event', lambda x,y: self._focus_out())
		self.entry.set_max_length(int(attrs.get('size',16)))
		self.entry.set_visibility(not attrs.get('invisible', False))

		self.button = self.win_gl.get_widget('button_url')
		self.button.connect('clicked', self.button_clicked)
		
		interface.widget_interface.__init__(self, window, parent=parent, attrs=attrs)

	def set_value(self, model,model_field):
		return model_field.set_client(model, self.entry.get_text() or False)

	def display(self, model, model_field):
		if not model_field:
			self.entry.set_text('')
			return False
		super(url, self).display(model, model_field)
		self.entry.set_text(model_field.get(model) or '')

	def _readonly_set(self, value):
		self.entry.set_editable(not value)
		self.entry.set_sensitive(not value)

	def button_clicked(self, widget):
		value = self.entry.get_text()
		if value:
			tools.launch_browser(value)

class email(url):
	def button_clicked(self, widget):
		value = self.entry.get_text()
		if value:
			tools.launch_browser('mailto:%s' % value)

# vim:noexpandtab:

