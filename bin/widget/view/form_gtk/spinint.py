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

import gtk
import sys
import ctypes
import interface
import tools
from tools import user_locale_format

class spinint(interface.widget_interface):

    def __init__(self, window, parent, model, attrs={}):
        interface.widget_interface.__init__(self, window, parent, model, attrs)

        adj = gtk.Adjustment(0.0, -sys.maxint, sys.maxint, 1.0, 5.0)
        self.widget = gtk.SpinButton(adj, 1, digits=0)
        self.widget.set_width_chars(5)
        self.widget.set_activates_default(True)
        self.widget.connect('populate-popup', self._menu_open)
        if self.attrs['readonly']:
            self._readonly_set(True)
        self.widget.connect('focus-in-event', lambda x,y: self._focus_in())
        self.widget.connect('focus-out-event', lambda x,y: self._focus_out())
        self.widget.connect('activate', self.sig_activate)
        self.widget.connect('input', self.format_input)
        self.widget.connect('output', self.format_output)

    def format_output(self, spin):
        digits = spin.get_digits()
        value = spin.get_value()
        text = user_locale_format.format('%.' + str(digits) + 'f', value)
        spin.set_text(text)
        return True

    def format_input(self, spin, new_value_pointer):
        text = spin.get_text()
        if text:
            value = user_locale_format.str2int(text)
            value_location = ctypes.c_double.from_address(hash(new_value_pointer))
            value_location.value = float(value)
            return True
        return False

    def set_value(self, model, model_field):
        self.widget.update()
        model_field.set_client(model, int(self.widget.get_value()))

    def display(self, model, model_field):
        if not model_field:
            self.widget.set_value(0)
            return False
        super(spinint, self).display(model, model_field)
        try:
            value = int(model_field.get(model))
            self.widget.set_value(value)
        except:
            self.widget.set_value(0)

    def _readonly_set(self, value):
        interface.widget_interface._readonly_set(self, value)
        self.widget.set_editable(not value)
        self.widget.set_sensitive(not value)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

