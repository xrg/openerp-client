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
    yoptions = gtk.FILL

    def __init__(self, rows = 2, cols = 2):
        Element.__init__(self, gtk.Table(rows, cols))
        self.n_rows     = 0
        self.n_cols     = 0
        self.entry_rows = None
        self.entry_cols = None
        self.targets    = {}
        self.child.set_row_spacings(3)
        self.child.set_col_spacings(3)
        self._resize_table(rows, cols)


    def _add_target(self, row, col):
        key    = '%d/%d' % (row, col)
        target = self.targets.get(key)
        if target is None:
            target = Target()
            target.connect('child-attached', self._on_target_child_attached)
            target.connect('child-removed',  self._on_target_child_removed)
            target.set_data('row', row)
            target.set_data('col', col)
            self.targets[key] = target
        self.child.attach(target, col, col + 1, row, row + 1)
        if target.element is not None:
            child = target.element
            self.child.child_set_property(target, 'x-options', child.xoptions)
            self.child.child_set_property(target, 'y-options', child.yoptions)
        target.show_all()


    def _resize_table(self, rows, cols):
        old_rows, old_cols = self.n_rows, self.n_cols

        # Remove useless targets.
        for child in self.child.get_children():
            if child.get_data('row') >= rows or child.get_data('col') >= cols:
                self.child.remove(child)

        # Add new targets.
        self.child.resize(rows, cols)
        for row in range(old_rows, rows):
            for col in range(0, old_cols):
                self._add_target(row, col)
        for col in range(old_cols, cols):
            for row in range(0, rows):
                self._add_target(row, col)

        self.n_rows, self.n_cols = rows, cols


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
        self.child.child_set_property(target, 'x-options', gtk.EXPAND|gtk.FILL)
        self.child.child_set_property(target, 'y-options', gtk.EXPAND|gtk.FILL)


    def get_pref_widget(self):
        label_rows      = gtk.Label('Rows:')
        self.entry_rows = gtk.SpinButton()
        label_cols      = gtk.Label('Columns:')
        self.entry_cols = gtk.SpinButton()
        table           = gtk.Table(2, 2)
        table.attach(label_rows, 0, 1, 0, 1, gtk.FILL)
        table.attach(self.entry_rows, 1, 2, 0, 1, gtk.EXPAND|gtk.FILL)
        table.attach(label_cols, 0, 1, 1, 2, gtk.FILL)
        table.attach(self.entry_cols, 1, 2, 1, 2, gtk.EXPAND|gtk.FILL)
        table.set_row_spacings(3)
        table.set_col_spacings(6)
        label_rows.set_alignment(0, .5)
        label_cols.set_alignment(0, .5)
        self.entry_rows.set_increments(1, 2)
        self.entry_cols.set_increments(1, 2)
        self.entry_rows.set_range(1, 20)
        self.entry_cols.set_range(1, 20)
        self.entry_rows.set_value(self.n_rows)
        self.entry_cols.set_value(self.n_cols)
        self.entry_rows.set_width_chars(1)
        self.entry_cols.set_width_chars(1)
        self.entry_rows.connect('changed', self._on_pref_size_changed)
        self.entry_cols.connect('changed', self._on_pref_size_changed)
        return table


    def _on_pref_size_changed(self, entry):
        rows = self.entry_rows.get_value_as_int()
        cols = self.entry_cols.get_value_as_int()
        self._resize_table(rows, cols)
