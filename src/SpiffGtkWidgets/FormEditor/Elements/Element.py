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
        # x and y are passed in FloatBox space
        alloc = self.get_allocation()
        if x > alloc.width  - 10 and x < alloc.width and \
           y > alloc.height - 10 and y < alloc.width:
            return True
        return False


    def get_pref_widget(self):
        label = gtk.Label('%s has no preferences' % self.caption)
        label.set_line_wrap(True)
        return label
