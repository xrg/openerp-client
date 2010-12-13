# Copyright (C) 2009-2011 Samuel Abels
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

class Preferences(gtk.Table):
    def __init__(self, element):
        gtk.Table.__init__(self, 2, 2)
        self.element    = element
        label_rows      = gtk.Label('Rows:')
        self.entry_rows = gtk.SpinButton()
        label_cols      = gtk.Label('Columns:')
        self.entry_cols = gtk.SpinButton()
        self.attach(label_rows, 0, 1, 0, 1, gtk.FILL, 0)
        self.attach(self.entry_rows, 1, 2, 0, 1, gtk.EXPAND|gtk.FILL, 0)
        self.attach(label_cols, 0, 1, 1, 2, gtk.FILL, 0)
        self.attach(self.entry_cols, 1, 2, 1, 2, gtk.EXPAND|gtk.FILL, 0)
        self.set_row_spacings(3)
        self.set_col_spacings(6)
        label_rows.set_alignment(0, .5)
        label_cols.set_alignment(0, .5)
        self.entry_rows.set_increments(1, 2)
        self.entry_cols.set_increments(1, 2)
        self.entry_rows.set_range(1, 20)
        self.entry_cols.set_range(1, 20)
        self.entry_rows.set_value(self.element.layout.n_rows)
        self.entry_cols.set_value(self.element.layout.n_cols)
        self.entry_rows.set_width_chars(1)
        self.entry_cols.set_width_chars(1)
        self.entry_rows.connect('changed', self._on_pref_size_changed)
        self.entry_cols.connect('changed', self._on_pref_size_changed)


    def _on_pref_size_changed(self, entry):
        rows = self.entry_rows.get_value_as_int()
        cols = self.entry_cols.get_value_as_int()
        self.element._resize_table(rows, cols)
