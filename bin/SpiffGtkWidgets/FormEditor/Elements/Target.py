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
from SpiffGtkWidgets.color import to_gdk
from Element import Element

class Target(Element):
    def __init__(self):
        self.box = gtk.EventBox()
        Element.__init__(self, self.box)
        self.set_property('can-focus', True)
        self.box.set_border_width(3)
        self.clear()


    def is_target(self):
        return True


    def _drop_child(self):
        if self.box.child is None:
            return
        self.emit('child-removed', self.box.child)
        self.box.remove(self.box.child)


    def _update_border(self):
        if self.selected:
            color = self.get_style().mid[gtk.STATE_SELECTED]
        elif self.element is None or self.get_parent() is None:
            color = to_gdk('red')
        else:
            parent = self.get_parent()
            color  = parent.get_style().bg[gtk.STATE_NORMAL]
        self.modify_bg(gtk.STATE_NORMAL, color)


    def copy(self):
        target = Target()
        if self.element is not None:
            target.attach(self.element.copy())
        return target


    def clear(self):
        self._drop_child()
        label = gtk.Label('Drop a widget here')
        label.set_size_request(15, 15)
        label.show()
        self.box.add(label)
        self.element  = None
        self.selected = False
        self._update_border()


    def attach(self, element):
        element.set_size_request(-1, -1)
        replace = self.box.child is not None
        if replace:
            self.box.remove(self.box.child)
        self.box.add(element)
        self.element = element
        self._update_border()
        if replace:
            self.emit('child-replaced', element)
        else:
            self.emit('child-attached', element)


    def select(self):
        self.selected = True
        self.grab_focus()
        self._update_border()


    def unselect(self):
        self.selected = False
        self._update_border()


    def is_selected(self):
        return self.selected


    def target_at(self, x, y):
        alloc = self.get_allocation()
        if x < 0 or y < 0 or x > alloc.width or y > alloc.height:
            return None
        if self.element is None:
            return self
        x, y   = self.translate_coordinates(self.element, x, y)
        target = self.element.target_at(x, y)
        if target is not None:
            return target
        return self


    def get_element(self):
        return self.element


    def get_pref_widget(self):
        return gtk.Label()


gobject.signal_new('child-attached',
                   Target,
                   gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_PYOBJECT, ))

gobject.signal_new('child-removed',
                   Target,
                   gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_PYOBJECT, ))

gobject.signal_new('child-replaced',
                   Target,
                   gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_PYOBJECT, ))

gobject.type_register(Target)
