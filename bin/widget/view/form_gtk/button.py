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

import gtk

import interface

class button(interface.widget_interface):
    def __init__(self, window, parent, model, attrs={}):
        interface.widget_interface.__init__(self, window, parent, model, attrs)
        self.widget = gtk.Button()
        if attrs.get('icon', False):
            icon = gtk.Image()
            icon.set_from_stock(attrs['icon'], gtk.ICON_SIZE_BUTTON)
            self.widget.set_image(icon)

        self.widget.set_label(attrs['string'])
        self.widget.connect('clicked', self.sig_exec)

    def _value_get(self):
        return self.widget.get_label()

    def sig_exec(self, widget):
        self.trigger('button_clicked', attrs['name'])

    def _value_set(self, value):
        pass

    value = property(_value_get, _value_set, None,
      'The content of the widget or ValueError if not valid')


