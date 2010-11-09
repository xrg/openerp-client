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
from LayoutChild import LayoutChild

class Layout(object):
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
