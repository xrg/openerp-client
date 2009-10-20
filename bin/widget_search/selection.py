# -*- coding: utf-8 -*-
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
import gobject
import wid_int
import rpc
import tools

class selection(wid_int.wid_int):
    def __init__(self, name, parent, attrs={}, model=None):
        wid_int.wid_int.__init__(self, name, parent, attrs)

        self.widget = gtk.combo_box_entry_new_text()
        self.widget.child.set_editable(True)
        self.attrs = attrs
        self._selection = {}
        self.name = name
        
        if attrs.get('context',False):
            self.widget.child.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("turquoise"))
            self.widget.child.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("turquoise"))
            self.widget.set_tooltip_markup("This Field comes with a context")
#        else:
#            self.widget.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
#            self.widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))        
        if 'selection' in attrs:
            self.set_popdown(attrs.get('selection',[]))
            
    def set_popdown(self, selection):
        self.model = self.widget.get_model()
        self.model.clear()
        self._selection={}
        lst = []
        for (i,j) in selection:
            name = str(j)
            lst.append(name)
            self._selection[name]=i
        for l in lst:
            self.widget.append_text(l)
        if '' not in self._selection:
            self.widget.append_text('')
        return lst

    def _value_get(self):
        model = self.widget.get_model()
        index = self.widget.get_active()
        ctx = None
        if self.attrs.get('context',False):
            ctx = self.attrs['context']
          
        if index>=0:
            res = self._selection.get(model[index][0], False)
            if ctx:
                if rpc.session.context.get('search_context',False):
                    for k in tools.expr_eval(ctx, {'self':False}).keys():
                        if k in rpc.session.context['search_context'].keys():
                            del rpc.session.context['search_context'][k]
            if res:
                if ctx:
                    rpc.session.context['search_context'] = tools.expr_eval(ctx, {'self':res})
                return [(self.name,'=',res)]
        else:
            if ctx:
                if rpc.session.context.get('search_context',False):
                    for k in tools.expr_eval(ctx, {'self':False}).keys():
                        if k in rpc.session.context['search_context'].keys():
                            del rpc.session.context['search_context'][k]
                
            res = self.widget.child.get_text()
            if res:
                return [(self.name,'ilike',res)]
        return []

    def _value_set(self, value):
        if value==False:
            value=''
        for s in self._selection:
            if self._selection[s]==value:
                self.widget.child.set_text(s)

    def clear(self):
        self.widget.child.set_text('')

    value = property(_value_get, _value_set, None,
      'The content of the widget or ValueError if not valid')

    def _readonly_set(self, value):
        self.widget.set_sensitive(not value)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

