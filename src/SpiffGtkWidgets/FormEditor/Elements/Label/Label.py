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
import gobject, gtk, pango
from SpiffGtkWidgets.FormEditor.Elements import EntryBox

class Label(EntryBox):
    name     = 'label'
    caption  = 'Label'
    xoptions = gtk.FILL
    yoptions = gtk.FILL

    def __init__(self, *args):
        EntryBox.__init__(self, *args)
        self.child.set_has_frame(False)
        self._on_entry_changed(self.child)
        self.child.connect('changed', self._on_entry_changed)
        if len(args) == 0:
            self.child.set_text('Label:')


    def copy(self):
        return Label(self.child.get_text())


    def do_realize(self):
        color = self.get_style().bg[gtk.STATE_NORMAL]
        self.child.modify_base(gtk.STATE_NORMAL, color)
        return EntryBox.do_realize(self)


    def _on_entry_changed(self, entry):
        layout       = entry.get_layout()
        x_off, y_off = entry.get_layout_offsets()
        w, h         = layout.get_pixel_size()
        entry.set_size_request(2 * x_off + w, -1)

gobject.type_register(Label)
