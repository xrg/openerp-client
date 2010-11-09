# Copyright (C) 2009 Samuel Abels <http://debain.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License
# version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import gobject, gtk
from Layout import Layout
from SpiffGtkWidgets.FormEditor.Elements import Element, Target

class Table(Element):
    name     = 'table'
    caption  = 'Table'
    xoptions = gtk.EXPAND|gtk.FILL
    yoptions = gtk.FILL

    def __init__(self, rows = 2, cols = 2):
        Element.__init__(self, gtk.Table(rows, cols))
        self.layout     = Layout(0, 0)
        self.entry_rows = None
        self.entry_cols = None
        self.targets    = {}
        self.child.set_row_spacings(3)
        self.child.set_col_spacings(3)
        self._resize_table(rows, cols)


    def has_layout(self):
        return True


    def copy(self):
        widget = Table(self.layout.n_rows, self.layout.n_cols)
        for child in self.child.get_children():
            top   = self.child.child_get_property(child, 'top-attach')
            bot   = self.child.child_get_property(child, 'bottom-attach')
            lft   = self.child.child_get_property(child, 'left-attach')
            rgt   = self.child.child_get_property(child, 'right-attach')
            child = child.copy()
            widget.child.attach(child, lft, rgt, top, bot)
            widget.layout.add(child, lft, rgt, top, bot)
        return widget


    def reassign(self, widget, upper_left, lower_right):
        top = self.child.child_get_property(upper_left,  'top-attach')
        bot = self.child.child_get_property(lower_right, 'bottom-attach')
        lft = self.child.child_get_property(upper_left,  'left-attach')
        rgt = self.child.child_get_property(lower_right, 'right-attach')

        if top >= bot or lft >= rgt:
            return

        # Remove the old target.
        target = widget.get_parent_target()
        widget.unparent()
        self._remove_target(target)

        # Re-add it into the new cells.
        target = self._add_target(top, bot, lft, rgt)
        target.attach(widget)


    def _remove_target(self, target):
        self.layout.remove(target)
        self.child.remove(target)


    def _remove_targets_at(self, top, bot, lft, rgt):
        for row in range(top, bot):
            for col in range(lft, rgt):
                target = self.layout.get_widget_at(row, col)
                self.layout.remove(target)
                if target and target.parent:
                    self.child.remove(target)


    def _add_target(self, top, bot, lft, rgt):
        # Remove the old target, if any.
        self._remove_targets_at(top, bot, lft, rgt)

        # Create a new target.
        target = Target()
        target.connect('child-attached', self._on_target_child_attached)
        target.connect('child-removed',  self._on_target_child_removed)
        target.connect('child-replaced', self._on_target_child_replaced)
        target.set_data('row', top)
        target.set_data('col', lft)
        self.layout.add(target, lft, rgt, top, bot)
        self.child.attach(target, lft, rgt, top, bot)
        target.show_all()
        return target


    def _position_of(self, child):
        top = self.child.child_get_property(child, 'top-attach')
        bot = self.child.child_get_property(child, 'bottom-attach')
        lft = self.child.child_get_property(child, 'left-attach')
        rgt = self.child.child_get_property(child, 'right-attach')
        return lft, rgt, top, bot


    def _resize_table(self, rows, cols):
        old_rows, old_cols = self.layout.n_rows, self.layout.n_cols
        self.layout.resize(rows, cols)

        # Remove useless targets.
        for child in self.child.get_children():
            if child.get_data('row') >= rows or child.get_data('col') >= cols:
                self.child.remove(child)

        # Add new targets.
        self.child.resize(rows, cols)
        for row in range(old_rows, rows):
            for col in range(0, old_cols):
                self._add_target(row, row + 1, col, col + 1)
        for col in range(old_cols, cols):
            for row in range(0, rows):
                self._add_target(row, row + 1, col, col + 1)


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


    def _on_target_child_attached(self, target, child):
        self.child.child_set_property(target, 'x-options', child.xoptions)
        self.child.child_set_property(target, 'y-options', child.yoptions)


    def _on_target_child_removed(self, target, child):
        lft, rgt, top, bot = self._position_of(target)

        # Remove the target, as it may have a cellspan.
        self.child.remove(target)

        # Add new targets into each cell.
        for row in range(top, bot):
            for col in range(lft, rgt):
                self._add_target(row, row + 1, col, col + 1)


    def _on_target_child_replaced(self, target, child):
        self._on_target_child_attached(target, child)
