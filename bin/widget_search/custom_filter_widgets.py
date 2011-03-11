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
import wid_int
import calendar
from calendar import calendar,datetime
from spinbutton import spinbutton
from spinint import spinint
from selection import selection
import char
import checkbox
from reference import reference
import rpc

class char(char.char):
    def __init__(self, name, parent, attrs={}, search_callback=None):
        super(char,self).__init__(name, parent)
        self.operators = (['=', _('is')],
                          ['<>',_('is not')],
                          ['=', _('is Empty')],
                          ['<>',_('is not Empty')],
                          ['ilike', _('contains')],
                          ['not ilike', _('doesn\'t contain')])
        self.selected_oper = False
        self.selected_oper_text = False
        self.field_left = False
        self.widget.connect('activate', search_callback)

    def _value_get(self):
        text = self.widget.get_text() or False
        if self.selected_oper_text in [_('is Empty'), _('is not Empty')]:
            text = False
        return [(self.field_left, self.selected_oper, text)]

    def set_visibility(self):
        self.widget.show_all()
        self.widget.set_text('')
        if self.selected_oper_text in [_('is Empty'), _('is not Empty')]:
            self.widget.hide()

class many2one(wid_int.wid_int):
    def __init__(self, name, parent, attrs={}, search_callback=None):
        wid_int.wid_int.__init__(self, name, parent)
        self.attrs = attrs
        self.operators = (['=', _('is')],
                          ['<>',_('is not')],
                          ['=', _('is Empty')],
                          ['<>',_('is not Empty')],
                          ['ilike', _('contains')],
                          ['not ilike', _('doesn\'t contain')])

        self.widget = gtk.HBox(spacing=0)
        self.widget.set_property('sensitive', True)

        self.wid_text = gtk.Entry()
        self.wid_text.set_property('width-chars', 20)
        self.wid_text.connect('key_press_event', self.sig_key_press)
        self.wid_text.connect_after('activate', self.sig_activate)
        self.widget.pack_start(self.wid_text, expand=True, fill=True)

        self.but_find = gtk.Button()
        img = gtk.Image()
        img.set_from_stock('gtk-find', gtk.ICON_SIZE_BUTTON)
        self.but_find.set_image(img)
        self.but_find.set_relief(gtk.RELIEF_NONE)
        self.but_find.connect('clicked', self.sig_find)
        self.but_find.set_alignment(0.5, 0.5)
        self.but_find.set_property('can-focus', False)
        self.but_find.set_tooltip_text(_('Search a resource'))
        self.but_find.set_size_request(30,30)
        self.widget.pack_start(self.but_find, padding=2, expand=False, fill=False)

        self.selected_oper = False
        self.selected_oper_text = False
        self.field_left = False
        self.enter_pressed = False
        self.selected_value = False

    def sig_activate(self, widget, event=None, leave=False):
        if not self.selected_oper_text in  [_('contains'), _('doesn\'t contain')]:
            event = self.enter_pressed and True or event
            return self.sig_find(widget, event, leave=True)

    def sig_find(self, widget, event=None, leave=True):
        from modules.gui.window.win_search import win_search
        name_search = self.wid_text.get_text() or ''
        ids = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['relation'], 'name_search', name_search, [], 'ilike', rpc.session.context)
        win = win_search(self.attrs['relation'], sel_multi=False, ids=map(lambda x: x[0], ids), context=rpc.session.context, parent=self.parent)
        win.glade.get_widget('newbutton').hide()
        ids = win.go()
        if ids:
            self.selected_value = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['relation'], 'name_get', [ids[0]], rpc.session.context)[0]
            self.wid_text.set_text(self.selected_value[1])
        return

    def sig_key_press(self, widget, event, *args):
        self.enter_pressed = False
        if event.keyval == gtk.keysyms.F2:
            self.sig_activate(widget, event)
        elif event.keyval == gtk.keysyms.Tab:
            if not self.wid_text.get_text():
                return False
            return not self.sig_activate(widget, event, leave=True)
        elif event.keyval in (gtk.keysyms.KP_Enter,gtk.keysyms.Return):
            if self.wid_text.get_text():
                self.enter_pressed = True
        return False

    def _value_get(self):
        if self.selected_oper_text in [_('is'), _('is not')]:
            text = self.selected_value and self.selected_value[0] or False
        elif self.selected_oper_text in ['is Empty', 'is not Empty']:
            text = False
        else:
            text = self.wid_text.get_text()
        return [(self.field_left, self.selected_oper, text)]

    def set_visibility(self):
        self.widget.show_all()
        self.wid_text.set_text('')
        self.selected_value = False
        if self.selected_oper_text in [_('is Empty'), _('is not Empty')]:
            self.wid_text.hide()
            self.but_find.hide()
        elif not self.selected_oper_text in ['is', 'is not']:
            self.but_find.hide()

class one2many(many2one):
     def __init__(self, name, parent, attrs={}, search_callback=None):
         many2one.__init__(self, name, parent, attrs, search_callback=None)
         self.operators = (['=', _('is')],
                           ['<>',_('is not')],
                           ['=', _('is Empty')],
                           ['<>',_('is not Empty')])
class many2many(many2one):
     def __init__(self, name, parent, attrs={}, search_callback=None):
         many2one.__init__(self, name, parent, attrs, search_callback=None)
         self.operators = (['=', _('is')],
                           ['<>',_('is not')],
                           ['=', _('is Empty')],
                           ['<>',_('is not Empty')])


class checkbox(wid_int.wid_int):
    def __init__(self, name, parent, attrs={}, search_callback=None):
        wid_int.wid_int.__init__(self, name, parent)
        self.widget = gtk.CheckButton()
        self.widget.set_active(False)
        self.operators = (['=', _('Equals')],)
        self.selected_oper = False
        self.field_left = False

    def _value_get(self):
        return [(self.field_left, self.selected_oper, int(self.widget.get_active()))]

    def set_visibility(self):
        pass

class calendar(calendar):
    def __init__(self, name, parent, attrs={}, search_callback=None):
        super(calendar,self).__init__(name, parent)
        self.operators =  (['=', _('is')],
                          ['<>',_('is not')],
                          ['*', _('between')],
                          ['=', _('is Empty')],
                          ['<>',_('is not Empty')],
                          ['**', _('exclude range')])

        self.selected_oper = False
        self.selected_oper_text = False
        self.field_left = False
        self.entry1.connect('activate', search_callback)
        self.entry2.connect('activate', search_callback)

    def _value_get(self):
        val1 = self._date_get(self.entry1.get_text())
        val2 = self._date_get(self.entry2.get_text())
        if self.selected_oper_text == _('between'):
            domain = ['&', (self.field_left, '>=', val1),(self.field_left, '<=', val2)]
            return domain
        elif self.selected_oper_text == _('exclude range'):
            domain = ['|',(self.field_left, '<', val1),(self.field_left, '>', val2)]
            return domain
        elif self.selected_oper_text in [_('is Empty'), _('is not Empty')]:
            val1 = False
        domain = [(self.field_left, self.selected_oper, val1)]
        return domain

    def set_visibility(self):
        self.entry1.set_text(self.widget1.widget.initial_value)
        self.entry2.set_text(self.widget2.widget.initial_value)
        if self.selected_oper_text in [_('is Empty'), _('is not Empty')]:
            self.widget.hide_all()
        elif self.selected_oper_text in [_('is'), _('is not')]:
            self.widget.show_all()
            self.entry1.show()
            self.entry2.hide()
            self.label.hide()
            self.eb1.show()
            self.eb2.hide()
        else:
            self.widget.show_all()

class datetime(datetime):
    def __init__(self, name, parent, attrs={}, search_callback=None):
        super(datetime,self).__init__(name, parent)
        self.operators =  (['=', _('is')],
                          ['<>',_('is not')],
                          ['*', _('between')],
                          ['=', _('is Empty')],
                          ['<>',_('is not Empty')],
                          ['**', _('exclude range')])
        self.selected_oper = False
        self.selected_oper_text = False
        self.field_left = False
        self.entry1.connect('activate', search_callback)
        self.entry2.connect('activate', search_callback)


    def _value_get(self):
        val1 = self._date_get(self.entry1.get_text())
        val2 = self._date_get(self.entry2.get_text())
        if self.selected_oper_text == _('between'):
            domain = ['&', (self.field_left, '>=', val1),(self.field_left, '<=', val2)]
            return domain
        elif self.selected_oper_text == _('exclude range'):
            domain = ['|',(self.field_left, '<', val1),(self.field_left, '>', val2)]
            return domain
        elif self.selected_oper_text in [_('is Empty'), _('is not Empty')]:
            val1 = False
        domain = [(self.field_left, self.selected_oper, val1)]
        return domain

    def set_visibility(self):
        self.entry1.set_text(self.widget1.widget.initial_value)
        self.entry2.set_text(self.widget2.widget.initial_value)
        if self.selected_oper_text in [_('is Empty'), _('is not Empty')]:
            self.widget.hide_all()
        elif self.selected_oper_text in [_('is'), _('is not')]:
            self.widget.show_all()
            self.entry1.show()
            self.entry2.hide()
            self.label.hide()
            self.eb1.show()
            self.eb2.hide()
        else:
            self.widget.show_all()


class selection(selection):
    def __init__(self, name, parent, attrs={}, search_callback=None):
        selection_dict = {'selection':attrs.get('selection', {})}
        super(selection,self).__init__(name, parent, selection_dict)
        self.operators =  (['=', _('is')],
                          ['<>',_('is not')])
        self.selected_oper = False
        self.selected_oper_text = False
        self.field_left = False

    def _value_get(self):
        key = self._selection.get(self.widget.child.get_text(), False)
        return [(self.field_left, self.selected_oper,  key)]

    def set_visibility(self):
        self.widget.child.set_text('')
        pass

#
class spinbutton(spinbutton):
    def __init__(self, name, parent, attrs={}, search_callback=None):
        super(spinbutton,self).__init__(name, parent)
        self.operators = (['=', _('is equal to')],
                          ['<>',_('is not equal to')],
                          ['>',_('greater than')],
                          ['<',_('less than')],
                          ['>=',_('greater than equal to')],
                          ['<=',_('less than equal to')],
                          ['*',_('between')],
                          ['**',_('exclude range')])
        self.selected_oper = False
        self.selected_oper_text = False
        self.field_left = False
        self.spin1.connect('activate', search_callback)
        self.spin2.connect('activate', search_callback)


    def _value_get(self):
        self.spin1.update()
        self.spin2.update()
        val1 = self.spin1.get_value()
        val2 = self.spin2.get_value()
        if self.selected_oper_text == _('between'):
            domain = ['&', (self.field_left, '>=', val1),(self.field_left, '<=', val2)]
            return domain
        elif self.selected_oper_text == _('exclude range'):
            domain = ['|',(self.field_left, '<', val1),(self.field_left, '>', val2)]
            return domain
        domain = [(self.field_left, self.selected_oper, val1)]
        return domain

    def set_visibility(self):
        self.spin1.set_value(0.0)
        self.spin2.set_value(0.0)
        if self.selected_oper_text in [_('between'), _('exclude range')]:
            self.widget.show_all()
        else:
            self.spin2.hide()
            self.label.hide()

class spinint(spinint):
    def __init__(self, name, parent, attrs={}, search_callback=None):
        super(spinint,self).__init__(name, parent)
        self.operators = (['=', _('is equal to')],
                          ['<>',_('is not equal to')],
                          ['>',_('greater than')],
                          ['<',_('less than')],
                          ['>=',_('greater than equal to')],
                          ['<=',_('less than equal to')],
                          ['*',_('between')],
                          ['**',_('exclude range')])
        self.selected_oper = False
        self.selected_oper_text = False
        self.field_left = False
        self.spin1.connect('activate', search_callback)
        self.spin2.connect('activate', search_callback)

    def _value_get(self):
        self.spin1.update()
        self.spin2.update()
        val1 = self.spin1.get_value()
        val2 = self.spin2.get_value()
        if self.selected_oper_text == _('between'):
            domain = ['&', (self.field_left, '>=', val1),(self.field_left, '<=', val2)]
            return domain
        elif self.selected_oper_text == _('exclude range'):
            domain = ['|',(self.field_left, '<', val1),(self.field_left, '>', val2)]
            return domain
        domain = [(self.field_left, self.selected_oper, val1)]
        return domain

    def set_visibility(self):
        val1 = self.spin1.set_value(0)
        val2 = self.spin2.set_value(0)
        if self.selected_oper_text in [_('between'), _('exclude range')]:
            self.widget.show_all()
        else:
            self.spin2.hide()
            self.label.hide()

widgets_type = {
    'date': calendar,
    'datetime': datetime,
    'float': spinbutton,
    'integer': spinint,
    'selection': selection,
    'char': char,
    'boolean': checkbox,
    'text': char,
    'many2one':many2one,
    'one2many':one2many,
    'many2many':many2many,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: