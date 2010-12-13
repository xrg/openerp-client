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
from SpiffGtkWidgets.FormEditor.Elements import Element

class Button(Element):
    name     = 'button'
    caption  = 'Button'
    xoptions = gtk.FILL
    yoptions = gtk.FILL

    def __init__(self, *args):
        Element.__init__(self, gtk.Button(*args))
        self.entry = gtk.Entry()
        align      = gtk.Alignment(.5, .5, 0, 0)
        align.add(self.entry)
        self.child.add(align)
        self.entry.set_has_frame(False)
        self.entry.connect('realize',              self._on_entry_realize)
        self.entry.connect('changed',              self._on_entry_changed)
        self.child.connect('focus-in-event',       self._on_button_focus)
        self.child.connect('button-press-event',   self._forward_event_to_parent)
        self.child.connect('button-press-event',   self._forward_event_to_entry)
        self.child.connect('button-release-event', self._forward_event_to_parent)
        if len(args) == 0:
            self.entry.set_text('Button')


    def copy(self):
        return Button(self.child.get_label())


    def _on_entry_realize(self, entry):
        color = self.child.get_style().bg[gtk.STATE_NORMAL]
        self.entry.modify_base(gtk.STATE_NORMAL, color)
        self.entry.add_events(gtk.gdk.BUTTON_PRESS_MASK)


    def _on_button_focus(self, widget, event):
        self.entry.grab_focus()
        self.entry.select_region(0, 0)
        self.entry.event(event)


    def _forward_event_to_entry(self, widget, event):
        event.window     = self.entry.window
        entry_x, entry_y = widget.translate_coordinates(self.entry,
                                                        int(event.x),
                                                        int(event.y))
        event.x, event.y = float(entry_x), float(entry_y)
        self.entry.emit('button-press-event',   event)
        #self.entry.emit('button-release-event', event)
        #gtk.main_do_event(event)


    def _forward_event_to_parent(self, widget, event):
        event.window       = self.parent.window
        parent_x, parent_y = widget.translate_coordinates(self.parent,
                                                          int(event.x),
                                                          int(event.y))
        event.x, event.y   = float(parent_x), float(parent_y)
        gtk.main_do_event(event)


    def _on_entry_changed(self, entry):
        layout       = entry.get_layout()
        x_off, y_off = entry.get_layout_offsets()
        w, h         = layout.get_pixel_size()
        entry.set_size_request(2 * x_off + w, -1)
