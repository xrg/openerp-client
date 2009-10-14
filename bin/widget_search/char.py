# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
import rpc
import wid_int
import tools


class char(wid_int.wid_int):
    def __init__(self, name, parent, attrs={}):
        wid_int.wid_int.__init__(self, name, parent, attrs)
        self.attrs = attrs
        self.widget = gtk.Entry()
        self.widget.set_max_length(int(attrs.get('size',16)))
        self.widget.set_width_chars(5)
        self.widget.set_property('activates_default', True)
        if attrs.get('context',False):
            self.widget.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("turquoise"))
            self.widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("turquoise"))
            self.widget.set_tooltip_markup("This Field comes with a context")
#        else:
#            self.widget.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
#            self.widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))    

    def _value_get(self):
        s = self.widget.get_text()
        ctx = None
        if self.attrs.get('context',False):
            ctx = self.attrs['context']
        if s:
            if ctx:
                rpc.session.context['search_context'] = tools.expr_eval(ctx, {'self':s})
            return [(self.name,self.attrs.get('comparator','ilike'),s)]
        else:
            if ctx:
                if rpc.session.context.get('search_context',False):
                    for k in tools.expr_eval(ctx, {'self':False}).keys():
                        if k in rpc.session.context['search_context'].keys():
                            rpc.session.context['search_context'].pop(k)
        return []

    def _value_set(self, value):
        self.widget.set_text(value)

    value = property(_value_get, _value_set, None, _('The content of the widget or ValueError if not valid'))

    def clear(self):
        self.value = ''

    def _readonly_set(self, value):
        self.widget.set_editable(not value)
        self.widget.set_sensitive(not value)

    def sig_activate(self, fct):
        self.widget.connect_after('activate', fct)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

