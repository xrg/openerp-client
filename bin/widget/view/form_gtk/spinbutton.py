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
import sys
import interface


class spinbutton(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		interface.widget_interface.__init__(self, window, parent, model, attrs)

		adj = gtk.Adjustment(0.0, -sys.maxint, sys.maxint, 1.0, 5.0, 5.0)
		self.widget = gtk.SpinButton(adj, 1.0, digits=int( attrs.get('digits',(14,2))[1] ) )
		self.widget.set_numeric(True)
		self.widget.set_activates_default(True)
		self.widget.connect('button_press_event', self._menu_open)
		if self.attrs['readonly']:
			self._readonly_set(True)
		self.widget.connect('focus-in-event', lambda x,y: self._focus_in())
		self.widget.connect('focus-out-event', lambda x,y: self._focus_out())
		self.widget.connect('activate', self.sig_activate)

	def set_value(self, model, model_field):
		self.widget.update()
		model_field.set_client(model, self.widget.get_value())

	def display(self, model, model_field):
		if not model_field:
			self.widget.set_value( 0.0 )
			return False
		super(spinbutton, self).display(model, model_field)
		value = model_field.get(model) or 0.0
		self.widget.set_value( float(value) )

	def _readonly_set(self, value):
		self.widget.set_editable(not value)
		self.widget.set_sensitive(not value)

