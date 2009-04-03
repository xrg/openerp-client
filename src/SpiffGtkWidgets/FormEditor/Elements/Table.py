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

class LayoutChild(object):
    left   = -1
    right  = -1
    top    = -1
    bottom = -1
    widget = None

    def __init__(self, widget):
        self.widget = widget


    def copy(self):
        child        = LayoutChild(self.widget.copy())
        child.left   = self.left
        child.right  = self.right
        child.top    = self.top
        child.bottom = self.bottom
        return child


class TableLayout(object):
    def __init__(self, rows, cols):
        self.n_rows = 0
        self.n_cols = 0
        self.matrix = {}
        self.resize(rows, cols)


    def _clear(self, left, right, top, bottom):
        for row in range(top, bottom):
            for col in range(left, right):
                key              = '%d/%d' % (row, col)
                self.matrix[key] = None


    def _get_maxwidth(self, col):
        width = 0
        for row in range(0, self.n_rows):
            key   = '%d/%d' % (row, col)
            child = self.matrix[key]
            if child is None:
                continue
            width = max(width, child.widget.get_allocation().width)
        return width


    def _get_maxheight(self, row):
        height = 0
        for row in range(0, self.n_cols):
            key   = '%d/%d' % (row, col)
            child = self.matrix[key]
            if child is None:
                continue
            height = max(height, child.widget.get_allocation().height)
        return height


    def resize(self, rows, cols):
        """
        x x x x
        x x x x
        x x x x
        x x x x
        """
        old_rows, old_cols = self.n_rows, self.n_cols

        # Remove useless targets.
        for row in range(rows, old_rows):
            for col in range(0, old_cols):
                del self.matrix['%d/%d' % (row, col)]
        for col in range(cols, old_cols):
            for row in range(0, rows):
                del self.matrix['%d/%d' % (row, col)]

        # Add new targets.
        for row in range(old_rows, rows):
            for col in range(0, old_cols):
                self.matrix['%d/%d' % (row, col)] = None
        for col in range(old_cols, cols):
            for row in range(0, rows):
                self.matrix['%d/%d' % (row, col)] = None

        self.n_rows, self.n_cols = rows, cols


    def add(self, widget, left, right, top, bottom):
        assert left < right  and right  <= self.n_cols
        assert top  < bottom and bottom <= self.n_rows

        child        = LayoutChild(widget)
        child.left   = left
        child.right  = right
        child.top    = top
        child.bottom = bottom

        for row in range(top, bottom):
            for col in range(left, right):
                key              = '%d/%d' % (row, col)
                self.matrix[key] = child


    def remove(self, widget):
        if widget is None:
            return
        for row in range(0, self.n_rows):
            for col in range(0, self.n_cols):
                key   = '%d/%d' % (row, col)
                child = self.matrix[key]
                if child is None or child.widget != widget:
                    continue
                self._clear(child.left, child.right, child.top, child.bottom)
                return


    def get_widget_at(self, row, col):
        key   = '%d/%d' % (row, col)
        child = self.matrix[key]
        if child is None:
            return None
        return child.widget


    def get_column_width(self, col):
        minspan = self.n_cols
        width   = self._get_maxwidth(col)
        for row in range(0, self.n_rows):
            key   = '%d/%d' % (row, col)
            child = self.matrix[key]
            if child is None:
                continue
            minspan = min(minspan, child.right - child.left)
            width   = min(width,   child.widget.get_allocation().width)
        return int(width / minspan)


    def get_row_height(self, row):
        minspan = self.n_rows
        height  = self._get_maxheight(row)
        for col in range(0, self.n_cols):
            key   = '%d/%d' % (row, col)
            child = self.matrix[key]
            if child is None:
                continue
            minspan = min(minspan, child.bottom - child.top)
            height  = min(height,  child.widget.get_allocation().height)
        return int(height / minspan)


    def copy(self):
        layout = TableLayout(self.n_rows, self.n_cols)
        done   = {}
        for pos, child in self.matrix.iteritems():
            if child not in done.keys():
                done[child] = child.copy()
            layout.matrix[pos] = done[child]
        return layout


class Table(Element):
    name     = 'table'
    caption  = 'Table'
    xoptions = gtk.EXPAND|gtk.FILL
    yoptions = gtk.FILL

    def __init__(self, rows = 2, cols = 2):
        Element.__init__(self, gtk.Table(rows, cols))
        self.layout     = TableLayout(0, 0)
        self.entry_rows = None
        self.entry_cols = None
        self.targets    = {}
        self.child.set_row_spacings(3)
        self.child.set_col_spacings(3)
        self._resize_table(rows, cols)


    def has_layout(self):
        return True


    def copy(self):
        widget        = Table(self.layout.n_rows, self.layout.n_cols)
        widget.layout = self.layout.copy()


    def reassign(self, widget, upper_left, lower_right):
        top = self.child.child_get_property(upper_left,  'top-attach')
        bot = self.child.child_get_property(lower_right, 'bottom-attach')
        lft = self.child.child_get_property(upper_left,  'left-attach')
        rgt = self.child.child_get_property(lower_right, 'right-attach')

        if top >= bot or lft >= rgt:
            return

        # Remove the old target.
        target = widget.parent.parent
        widget.unparent()
        self._remove_target(target)
        self._remove_targets_at(top, bot, lft, rgt)

        # Re-add it into the new cells.
        target = self._add_target(top, lft, bot, rgt)
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


    def _add_target(self, top, lft, bot = None, rgt = None):
        if bot is None:
            bot = top + 1
        if rgt is None:
            rgt = lft + 1

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
                self._add_target(row, col)
        for col in range(old_cols, cols):
            for row in range(0, rows):
                self._add_target(row, col)


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
                self._add_target(row, col)
        #self.child.child_set_property(target, 'x-options', gtk.EXPAND|gtk.FILL)
        #self.child.child_set_property(target, 'y-options', gtk.EXPAND|gtk.FILL)


    def _on_target_child_replaced(self, target, child):
        self.child.child_set_property(target, 'x-options', child.xoptions)
        self.child.child_set_property(target, 'y-options', child.yoptions)
        #self.child.child_set_property(target, 'x-options', gtk.EXPAND|gtk.FILL)
        #self.child.child_set_property(target, 'y-options', gtk.EXPAND|gtk.FILL)
        pass


    def get_pref_widget(self):
        label_rows      = gtk.Label('Rows:')
        self.entry_rows = gtk.SpinButton()
        label_cols      = gtk.Label('Columns:')
        self.entry_cols = gtk.SpinButton()
        table           = gtk.Table(2, 2)
        table.attach(label_rows, 0, 1, 0, 1, gtk.FILL, 0)
        table.attach(self.entry_rows, 1, 2, 0, 1, gtk.EXPAND|gtk.FILL, 0)
        table.attach(label_cols, 0, 1, 1, 2, gtk.FILL, 0)
        table.attach(self.entry_cols, 1, 2, 1, 2, gtk.EXPAND|gtk.FILL, 0)
        table.set_row_spacings(3)
        table.set_col_spacings(6)
        label_rows.set_alignment(0, .5)
        label_cols.set_alignment(0, .5)
        self.entry_rows.set_increments(1, 2)
        self.entry_cols.set_increments(1, 2)
        self.entry_rows.set_range(1, 20)
        self.entry_cols.set_range(1, 20)
        self.entry_rows.set_value(self.layout.n_rows)
        self.entry_cols.set_value(self.layout.n_cols)
        self.entry_rows.set_width_chars(1)
        self.entry_cols.set_width_chars(1)
        self.entry_rows.connect('changed', self._on_pref_size_changed)
        self.entry_cols.connect('changed', self._on_pref_size_changed)
        return table


    def _on_pref_size_changed(self, entry):
        rows = self.entry_rows.get_value_as_int()
        cols = self.entry_cols.get_value_as_int()
        self._resize_table(rows, cols)
