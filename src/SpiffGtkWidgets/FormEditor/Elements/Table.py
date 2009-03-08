# Copyright (C) 2009 Samuel Abels <http://debain.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import gobject, gtk
from Target  import Target
from Element import Element

class Table(Element):
    name     = 'table'
    caption  = 'Table'
    xoptions = gtk.EXPAND|gtk.FILL
    yoptions = gtk.EXPAND|gtk.FILL

    def __init__(self, rows = 2, cols = 2):
        Element.__init__(self, gtk.Table(rows, cols))
        self.child.set_row_spacings(3)
        self.child.set_col_spacings(6)
        self._resize_table(rows, cols)


    def _resize_table(self, rows, cols):
        self.child.resize(rows, cols)
        for row in range(0, self.child.get_property('n-rows')):
            for col in range(0, self.child.get_property('n-columns')):
                target = Target()
                target.connect('child-attached', self._on_target_child_attached)
                target.connect('child-removed',  self._on_target_child_removed)
                self.child.attach(target, row, row + 1, col, col + 1)


    def _child_at(self, x, y):
        for child in self.child.get_children():
            child_x, child_y = self.translate_coordinates(child, x, y)
            if child_x < 0 or child_y < 0:
                continue
            alloc = child.get_allocation()
            if child_x > alloc.width or child_y > alloc.height:
                continue
            return child
        return None


    def target_at(self, x, y):
        child = self._child_at(x, y)
        if child is None:
            return None
        child_x, child_y = self.translate_coordinates(child, x, y)
        target           = child.target_at(child_x, child_y)
        if target is not None:
            return target
        return child


    def element_at(self, x, y):
        child = self._child_at(x, y)
        if child is None:
            return self
        child_x, child_y = self.translate_coordinates(child, x, y)
        element          = child.element_at(child_x, child_y)
        if element is not None:
            return element
        return self


    def _on_target_child_attached(self, target, child):
        self.child.child_set_property(target, 'x-options', child.xoptions)
        self.child.child_set_property(target, 'y-options', child.yoptions)


    def _on_target_child_removed(self, target, child):
        self.child.child_set_property(target, 'x-options', gtk.EXPAND|gtk.FILL)
        self.child.child_set_property(target, 'y-options', gtk.EXPAND|gtk.FILL)
