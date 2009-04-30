# -*- coding: UTF-8 -*-
# Copyright (C) 2004,2005 by SICEm S.L.
# Copyright (C) 2005 Red Hat, Inc.
# Copyright (C) 2006 Async Open Source
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
import gobject, gtk, pango

class Element(gtk.EventBox):
    """
    Attributes of a child widget stored in a FloatBox.
    """
    DECORATION_PAD = 1

    def __init__(self, widget):
        gtk.EventBox.__init__(self)
        self.add(widget)

        # Coordinates are in the space of the FormEditor.
        self.x = 0
        self.y = 0
        self.compute_size()
        widget.add_events(gtk.gdk.POINTER_MOTION_MASK)
        widget.connect('motion-notify-event', self._on_motion_notify)


    def has_layout(self):
        return False


    def get_parent_layout(self):
        widget = self.parent
        while widget:
            if isinstance(widget, Element) and widget.has_layout():
                return widget
            widget = widget.parent
        return None


    def is_target(self):
        return False


    def get_parent_target(self):
        widget = self.parent
        while widget:
            if isinstance(widget, Element) and widget.is_target():
                return widget
            widget = widget.parent
        return None


    def copy(self):
        raise AssertionError('no such operation')


    def compute_size(self):
        w, h                   = self.size_request()
        self.decoration_x      = self.x - self.DECORATION_PAD
        self.decoration_y      = self.y - self.DECORATION_PAD
        self.decoration_width  = w + self.DECORATION_PAD * 2
        self.decoration_height = h + self.DECORATION_PAD * 2


    def target_at(self, x, y):
        return None


    def in_drag_area(self, x, y):
        alloc = self.get_allocation()
        if x < 0 or y < 0 or x > alloc.width or y > alloc.height:
            return False
        return True


    def in_resize_area(self, x, y):
        alloc = self.get_allocation()
        if x >= alloc.width  - 15 and x <= alloc.width + 3 and \
           y >= alloc.height - 15 and y <= alloc.height + 3:
            return True
        return False


    def _on_motion_notify(self, widget, event):
        if self.in_resize_area(event.x, event.y):
            cursor = gtk.gdk.Cursor(gtk.gdk.BOTTOM_RIGHT_CORNER)
            self.window.set_cursor(cursor)
        else:
            self.window.set_cursor(None)


    def get_pref_widget(self):
        module = __import__('.'.join(self.__module__.split('.')[:-1]),
                            globals(),
                            locals(),
                            self.__module__)
        try:
            prefs = module.Preferences
        except:
            label = gtk.Label('%s has no preferences' % self.caption)
            label.set_line_wrap(True)
            return label
        return prefs(self)
