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
import common
import wid_int
import sys
import tools

class spinbutton(wid_int.wid_int):
    def __init__(self, name, parent, attrs={},screen=None):
        wid_int.wid_int.__init__(self, name, parent, attrs, screen)

        self.widget = gtk.HBox(spacing=3)

        adj1 = gtk.Adjustment(0.0, -sys.maxint, sys.maxint, 1.0, 5.0)
        self.spin1 = gtk.SpinButton(adj1, 1.0, digits=int(attrs.get('digits', (14, 2))[1]))
        self.spin1.set_numeric(True)
        self.spin1.set_activates_default(True)
        self.widget.pack_start(self.spin1, expand=False, fill=True)

        self.widget.pack_start(gtk.Label('-'), expand=False, fill=False)

        adj2 = gtk.Adjustment(0.0, -sys.maxint, sys.maxint, 1.0, 5.0)
        self.spin2 = gtk.SpinButton(adj2, 1.0, digits=int(attrs.get('digits', (14, 2))[1]))
        self.spin2.set_numeric(True)
        self.spin2.set_activates_default(True)
        self.widget.pack_start(self.spin2, expand=False, fill=True)

        if self.default_search:
            self.spin1.set_value(self.default_search)

    def _value_get(self):
        res = []
        self.spin1.update()
        self.spin2.update()
        if self.spin1.get_value() > self.spin2.get_value():
            if self.spin2.get_value() != 0.0:
                res.append((self.name, '>=', self.spin2.get_value()))
                res.append((self.name, '<=', self.spin1.get_value()))
            else:
                res.append((self.name, '>=', self.spin1.get_value()))
        elif self.spin2.get_value() > self.spin1.get_value():
            res.append((self.name, '<=', self.spin2.get_value()))
            res.append((self.name, '>=', self.spin1.get_value()))
        elif (self.spin2.get_value() == self.spin1.get_value()) and (self.spin1.get_value() != 0.0):
            res.append((self.name, '=', self.spin1.get_value()))
        return {'domain':res}

    def _value_set(self, value):
        self.spin1.set_value(value)
        self.spin2.set_value(value)

    value = property(_value_get, _value_set, None, _('The content of the widget or ValueError if not valid'))

    def clear(self):
        self.value = 0.00

    def sig_activate(self, fct):
        self.spin1.connect_after('activate', fct)
        self.spin2.connect_after('activate', fct)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

