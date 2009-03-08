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

class FormEditorChild(gtk.EventBox):
    """
    Attributes of a child widget stored in a FormEditor
    """
    DECORATION_PAD = 1

    def __init__(self, widget):
        gtk.EventBox.__init__(self)
        self.set_above_child(True)
        self.add(widget)

        # All coordinates are in the space of the FormEditor.
        self.x                 = 0
        self.y                 = 0
        self.decoration_x      = 0
        self.decoration_y      = 0
        self.decoration_width  = 1
        self.decoration_height = 1


    def compute_size(self):
        w, h                   = self.size_request()
        self.decoration_x      = self.x - self.DECORATION_PAD
        self.decoration_y      = self.y - self.DECORATION_PAD
        self.decoration_width  = w + self.DECORATION_PAD * 2
        self.decoration_height = h + self.DECORATION_PAD * 2


    def in_drag_area(self, x, y):
        # x and y are passed in FormEditor space
        if x < self.decoration_x:
            return False
        elif x > self.decoration_x + self.decoration_width:
            return False
        elif y < self.decoration_y:
            return False
        elif y > self.decoration_y + self.decoration_height:
            return False
        return True


    def in_resize_area(self, x, y):
        # x and y are passed in FormEditor space
        if (x > (self.decoration_x +
                 self.decoration_width -
                 self.DECORATION_PAD) and
            y > (self.decoration_y +
                 self.decoration_height -
                 self.DECORATION_PAD)):
            return True
        return False
