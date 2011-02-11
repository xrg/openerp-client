# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
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


class char(char.char):
    def __init__(self, name, parent, attrs={}, screen=None):
        super(char,self).__init__(name, parent, attrs, screen)
        self.operators = (['=', _('is')],
                          ['<>',_('is not')],
                          ['=', _('is Empty')],
                          ['<>',_('is not Empty')],
                          ['ilike', _('contains')],
                          ['not ilike', _('doesn\'t contain')])
        self.selected_oper = False
        self.selected_oper_text = False
        self.field_left = False

    def _value_get(self):
        if self.selected_oper_text in ['is Empty', 'is not Empty']:
            text = False
        else:
            text = self.widget.get_text()
        return [(self.field_left, self.selected_oper, text)]

    def set_visibility(self):
        if self.selected_oper_text in ['is Empty', 'is not Empty']:
            self.widget.hide()
        else:
            self.widget.show()

class many2one(wid_int.wid_int):
    def __init__(self, name, parent, attrs={}, screen=None):
        wid_int.wid_int.__init__(self, name, parent, attrs, screen)
        self.operators = (['=', _('is')],
                          ['<>',_('is not')],
                          ['=', _('is Empty')],
                          ['<>',_('is not Empty')],
                          ['ilike', _('contains')],
                          ['like', _('like')],
                          ['not ilike', _('doesn\'t contain')])

        self.widget = gtk.HBox(spacing=0)
        self.widget.set_property('sensitive', True)

        self.wid_text = gtk.Entry()
        self.wid_text.set_property('width-chars', 13)
        self.wid_text.connect('key_press_event', self.sig_key_press)
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

    def sig_find(self, widget, event=None, leave=True):
        return

    def sig_key_press(self, widget, event, *args):
        return

    def _value_get(self):
        if self.selected_oper_text in ['is Empty', 'is not Empty']:
            text = False
        else:
            text = self.widget.get_text()
        return [(self.field_left, self.selected_oper, text)]

    def set_visibility(self):
        if self.selected_oper_text in ['is Empty', 'is not Empty']:
            self.widget.hide()
        else:
            self.widget.show()

class checkbox(wid_int.wid_int):
    def __init__(self, name, parent, attrs={}, screen=None):
        wid_int.wid_int.__init__(self, name, parent, attrs, screen)
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
    def __init__(self, name, parent, attrs={}, screen=None):
        super(calendar,self).__init__(name, parent, attrs, screen)
        self.operators =  (['=', _('is')],
                          ['<>',_('is not')],
                          ['*', _('between')],
                          ['=', _('is Empty')],
                          ['<>',_('is not Empty')],
                          ['**', _('exclude range')])

        self.selected_oper = False
        self.selected_oper_text = False
        self.field_left = False

    def _value_get(self):
        val1 = self._date_get(self.entry1.get_text())
        val2 = self._date_get(self.entry2.get_text())
        if self.selected_oper_text == 'between':
            domain = ('&', (self.field_left, '>=', val1),(self.field_left, '<=', val2))
            return domain
        elif self.selected_oper_text == 'exclude range':
            domain = ('|',(self.field_left, '<', val1),(self.field_left, '>', val2))
            return domain
        elif self.selected_oper_text in ['is Empty', 'is not Empty']:
            val1 = False
        domain = [(self.field_left, self.selected_oper, val1)]
        return domain

    def set_visibility(self):
        if self.selected_oper_text in ['is Empty', 'is not Empty']:
            self.widget.hide_all()
        elif self.selected_oper_text in ['is', 'is not']:
            self.widget.show_all()
            self.entry1.show()
            self.entry2.hide()
            self.label.hide()
            self.eb1.show()
            self.eb2.hide()
        else:
            self.widget.show_all()

class datetime(datetime):
    def __init__(self, name, parent, attrs={}, screen=None):
        super(datetime,self).__init__(name, parent, attrs, screen)
        self.operators =  (['=', _('is')],
                          ['<>',_('is not')],
                          ['*', _('between')],
                          ['=', _('is Empty')],
                          ['<>',_('is not Empty')],
                          ['**', _('exclude range')])
        self.selected_oper = False
        self.selected_oper_text = False
        self.field_left = False

    def _value_get(self):
        val1 = self._date_get(self.entry1.get_text())
        val2 = self._date_get(self.entry2.get_text())
        if self.selected_oper_text == 'between':
            domain = ('&', (self.field_left, '>=', val1),(self.field_left, '<=', val2))
            return domain
        elif self.selected_oper_text == 'exclude range':
            domain = ('|',(self.field_left, '<', val1),(self.field_left, '>', val2))
            return domain
        elif self.selected_oper_text in ['is Empty', 'is not Empty']:
            val1 = False
        domain = [(self.field_left, self.selected_oper, val1)]
        return domain

    def set_visibility(self):
        if self.selected_oper_text in ['is Empty', 'is not Empty']:
            self.widget.hide_all()
        elif self.selected_oper_text in ['is', 'is not']:
            self.widget.show_all()
            self.entry1.show()
            self.entry2.hide()
            self.label.hide()
            self.eb1.show()
            self.eb2.hide()
        else:
            self.widget.show_all()


class selection(selection):
    def __init__(self, name, parent, attrs={}, model=None, screen=None):
        new_attrs = {}
        if attrs:
            new_attrs.update({'selection':attrs})
        super(selection,self).__init__(name, parent, new_attrs, screen)
        self.operators =  (['=', _('is')],
                          ['<>',_('is not')])
        self.selected_oper = False
        self.selected_oper_text = False
        self.field_left = False

    def _value_get(self):
        key = self._selection.get(self.widget.child.get_text(), False)
        return [(self.field_left, self.selected_oper,  key)]

    def set_visibility(self):
        pass

#
class spinbutton(spinbutton):
    def __init__(self, name, parent, attrs={},screen=None):
        super(spinbutton,self).__init__(name, parent, attrs, screen)
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

    def _value_get(self):
        self.spin1.update()
        self.spin2.update()
        val1 = self.spin1.get_value()
        val2 = self.spin2.get_value()
        if self.selected_oper_text == 'between':
            domain = ('&', (self.field_left, '>=', val1),(self.field_left, '<=', val2))
            return domain
        elif self.selected_oper_text == 'exclude range':
            domain = ('|',(self.field_left, '<', val1),(self.field_left, '>', val2))
            return domain
        domain = [(self.field_left, self.selected_oper, val1)]
        return domain

    def set_visibility(self):
        if self.selected_oper_text in ['between', 'exclude range']:
            self.widget.show_all()
        else:
            self.spin2.hide()
            self.label.hide()

class spinint(spinint):
    def __init__(self, name, parent, attrs={},screen=None):
        super(spinint,self).__init__(name, parent, attrs, screen)
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

    def _value_get(self):
        self.spin1.update()
        self.spin2.update()
        val1 = self.spin1.get_value()
        val2 = self.spin2.get_value()
        if self.selected_oper_text == 'between':
            domain = ('&', (self.field_left, '>=', val1),(self.field_left, '<=', val2))
            return domain
        elif self.selected_oper_text == 'exclude range':
            domain = ('|',(self.field_left, '<', val1),(self.field_left, '>', val2))
            return domain
        domain = [(self.field_left, self.selected_oper, val1)]
        return domain

    def set_visibility(self):
        if self.selected_oper_text in ['between', 'exclude range']:
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
    'many2one':char,
    'one2many':char,
    'many2many':char,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: