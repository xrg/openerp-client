# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import common
import interface

class char(interface.widget_interface):
    def __init__(self, window, parent, model, attrs={}):
        interface.widget_interface.__init__(self, window, parent, attrs=attrs)

        self.widget = gtk.Entry()
        self.widget.set_property('activates_default', True)
        self.widget.set_max_length(int(attrs.get('size',16)))
        self.widget.set_visibility(not attrs.get('password', False))
        self.widget.set_width_chars(5)

        self.widget.connect('button_press_event', self._menu_open)
        self.widget.connect('activate', self.sig_activate)
        self.widget.connect('focus-in-event', lambda x,y: self._focus_in())
        self.widget.connect('focus-out-event', lambda x,y: self._focus_out())

    def set_value(self, model, model_field):
        return model_field.set_client(model, self.widget.get_text() or False)

    def display(self, model, model_field):
        if not model_field:
            self.widget.set_text('')
            return False
        super(char, self).display(model, model_field)
        self.widget.set_text(model_field.get(model) or '')

    def _readonly_set(self, value):
        self.widget.set_editable(not value)
        #self.widget.set_sensitive(not value)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

