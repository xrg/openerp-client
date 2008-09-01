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

#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import pango
import re

import time
from mx.DateTime import RelativeDateTime
from mx.DateTime import DateTime
from mx.DateTime import now
from mx.DateTime import strptime


mapping = {
    '%y': ('__', '[_0-9][_0-9]'),
    '%Y': ('____', '[_1-9][_0-9][_0-9][_0-9]'),
    '%m': ('__', '[_0-1][_0-9]'),
    '%d': ('__', '[_0-3][_0-9]'),
    '%H': ('__', '[_0-2][_0-9]'),
    '%M': ('__', '[_0-6][_0-9]'),
    '%S': ('__', '[_0-6][_0-9]'),
}

class DecoratorRenderer(gtk.GenericCellRenderer):
    def __init__(self, renderer1, callback, format):
        self.__gobject_init__()
        self._renderer1 = renderer1
        self.set_property("mode", renderer1.get_property("mode"))
        self.callback = callback
        self.format = format
        self.regex = self.initial_value = self.format
        for key,val in mapping.items():
            self.regex = self.regex.replace(key, val[1])
            self.initial_value = self.initial_value.replace(key, val[0])

    def get_property(self, *args, **argv):
        return self._renderer1.get_property(*args, **argv)

    def set_property(self, *args, **argv):
        return self._renderer1.set_property(*args, **argv)

    def on_get_size(self, widget, cell_area=None):
        return self._renderer1.get_size(widget, cell_area)

    def on_render(self, window, widget, background_area, cell_area, expose_area, flags):
        return self._renderer1.render(window, widget, background_area, cell_area, expose_area, flags)
    
    def on_activate(self, event, widget, path, background_area, cell_area, flags):
        return self._renderer1.activate(event, widget, path, background_area, cell_area, flags)

    def on_start_editing(self, event, widget, path, background_area, cell_area, flags):
        print 'Start Editing'
        editable = self._renderer1.start_editing(event, widget, path, background_area, cell_area, flags)

        self.editable = editable
        editable.modify_font(pango.FontDescription("monospace"))

        editable.set_text(self.initial_value)
        self.regex = re.compile(self.regex)

        assert self.regex.match(self.initial_value), 'Error, the initial value should be validated by regex'
        editable.set_width_chars(len(self.initial_value))
        editable.set_max_length(len(self.initial_value))

        editable.connect('key-press-event', self._on_key_press)


        self._interactive_input = True
        self.mode_cmd = False
        gobject.idle_add(editable.set_position, 0)
        return editable

    def _on_delete_text(self, editable, start, end):
        while (start>0) and (self.initial_value[start] not in ['_','0','X']):
            start -= 1
        text = editable.get_text()
        text = text[:start] + self.initial_value[start:end] + text[end:]
        editable.set_text(text)
        gobject.idle_add(editable.set_position, start)
        return

    def date_get(self, editable):
        tt = time.strftime(self.format, time.localtime())
        tc = editable.get_text()
        if tc==self.initial_value:
            return False
        for a in range(len(self.initial_value)):
            if self.initial_value[a] == tc[a]:
                tc = tc[:a] + tt[a] + tc[a+1:]
        try:
            editable.set_text(tc)
            return strptime(tc, self.format)
        except:
            tc = tt
        editable.set_text(tc)
        return strptime(tc, self.format)

    def _on_key_press(self, editable, event):
        if event.keyval in (gtk.keysyms.Tab, gtk.keysyms.Escape, gtk.keysyms.Return):
            if self.mode_cmd:
                self.mode_cmd = False
                if self.callback: self.callback.process(self, event)
                #self.stop_emission("key-press-event")
                return True
        elif event.keyval in (ord('+'),ord('-'),ord('=')):
                self.mode_cmd = True
                self.date_get(editable)
                if self.callback: self.callback.event(self, event)
                #self.stop_emission("key-press-event")
                return True
        elif self.mode_cmd:
            if self.callback: self.callback.event(self, event)
            return True

        if event.keyval in (gtk.keysyms.BackSpace,):
            pos = editable.get_position()
            self._on_delete_text(editable, max(0,pos-1), pos)
            return True
        if event.keyval in (gtk.keysyms.Delete,):
            pos = editable.get_position()
            text = editable.get_text()
            self._on_delete_text(editable, pos, len(text))
            return True

        if event.keyval>=ord('0') and event.keyval<=ord('9'):
            pos = editable.get_position()
            text = editable.get_text()
            text = text[:pos] + chr(event.keyval) + text[pos + 1:]
            if self.regex.match(text):
                pos += 1
                while (pos<len(self.initial_value)) and (self.initial_value[pos] not in ['_','0','X']):
                    pos += 1
                editable.set_text(text)
                editable.show()
                gobject.idle_add(editable.set_position, pos)

        if not event.string:
            return False
        return True

    def date_set(self, dt):
        if dt:
            self.editable.set_text( dt.strftime(self.format) )
        else:
            self.editable.set_text(self.initial_value)


class date_callback(object):
    def __init__(self):
        self.value = ''

    def event(self, widget, event):
        if event.keyval in (gtk.keysyms.BackSpace,):
            self.value = self.value[:-1]
        if event.keyval<250:
            self.value = self.value+chr(event.keyval)
        self.display(widget)
        return True

    def display(self, widget):
        print self.value

    def process(self, widget, event):
        if (not event.keyval == gtk.keysyms.Escape) or not event:
            lst = {
                '^=(\d+)w$': lambda dt,r: dt+RelativeDateTime(day=0, month=0, weeks = int(r.group(1))),
                '^=(\d+)d$': lambda dt,r: dt+RelativeDateTime(day=int(r.group(1))),
                '^=(\d+)m$': lambda dt,r: dt+RelativeDateTime(day=0, month = int(r.group(1))),
                '^=(2\d\d\d)y$': lambda dt,r: dt+RelativeDateTime(year = int(r.group(1))),
                '^=(\d+)h$': lambda dt,r: dt+RelativeDateTime(hour = int(r.group(1))),
                '^([\\+-]\d+)h$': lambda dt,r: dt+RelativeDateTime(hours = int(r.group(1))),
                '^([\\+-]\d+)w$': lambda dt,r: dt+RelativeDateTime(days = 7*int(r.group(1))),
                '^([\\+-]\d+)d$': lambda dt,r: dt+RelativeDateTime(days = int(r.group(1))),
                '^([\\+-]\d+)m$': lambda dt,r: dt+RelativeDateTime(months = int(r.group(1))),
                '^([\\+-]\d+)y$': lambda dt,r: dt+RelativeDateTime(years = int(r.group(1))),
                '^=$': lambda dt,r: now(),
                '^-$': lambda dt,r: False
            }
            cmd = self.value
            for r,f in lst.items():
                groups = re.match(r, cmd)
                if groups:
                    dt = widget.date_get(widget.editable)
                    if not dt:
                        dt = time.strftime(widget.format, time.localtime())
                        dt = strptime(dt, widget.format)
                    widget.date_set(f(dt,groups))
                    break
        self.value = ''
        self.display(widget)

class TreeViewColumnExample:
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("TreeViewColumn Example")
        self.window.connect("delete_event", self.delete_event)
        self.liststore = gtk.ListStore(str, str, str, 'gboolean')
        self.treeview = gtk.TreeView(self.liststore)
        decorated = gtk.CellRendererText()
        decorated.set_property('editable', True)
        decorator = DecoratorRenderer(decorated, date_callback(), '%d/%m/%Y %H:%M:%S')

        # create the TreeViewColumns to display the data
        self.tvcolumn = gtk.TreeViewColumn('Pixbuf and Text', gtk.CellRendererText(), text=0)
        self.tvcolumn1 = gtk.TreeViewColumn('Text Only', decorator)

        self.liststore.append(['Open', gtk.STOCK_OPEN, 'Open a File', True])
        self.liststore.append(['New', gtk.STOCK_NEW, 'New File', True])
        self.liststore.append(['Print', gtk.STOCK_PRINT, 'Print File', False])

        # add columns to treeview
        self.treeview.append_column(self.tvcolumn)
        self.treeview.append_column(self.tvcolumn1)

        self.window.add(self.treeview)
        self.window.show_all()

def main():
    gtk.main()

if __name__ == "__main__":
    tvcexample = TreeViewColumnExample()
    main()


