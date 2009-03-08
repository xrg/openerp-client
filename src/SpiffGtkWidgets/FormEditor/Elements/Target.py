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
import gobject, gtk, pango
from SpiffGtkWidgets.color import to_gdk
from Element import Element

class Target(Element):
    def __init__(self):
        self.box = gtk.EventBox()
        Element.__init__(self, self.box)
        self.clear()


    def _drop_child(self):
        if self.box.child is None:
            return
        self.emit('child-removed', self.box.child)
        self.box.remove(self.box.child)


    def _update_border_width(self):
        if self.selected or self.element is None:
            self.box.set_border_width(2)
        else:
            self.box.set_border_width(0)


    def clear(self):
        self._drop_child()
        label = gtk.Label('Drop a widget here')
        label.set_size_request(15, 15)
        label.show()
        self.box.add(label)
        self.element  = None
        self.selected = False
        self.modify_bg(gtk.STATE_NORMAL, to_gdk('red'))
        self._update_border_width()


    def attach(self, element):
        element.set_size_request(-1, -1)
        self._drop_child()
        self.box.add(element)
        self.element = element
        self._update_border_width()
        self.emit('child-attached', element)


    def select(self):
        self.selected = True
        color = self.get_style().mid[gtk.STATE_SELECTED]
        self.modify_bg(gtk.STATE_NORMAL, color)
        self._update_border_width()


    def unselect(self):
        self.selected = False
        self.modify_bg(gtk.STATE_NORMAL, to_gdk('red'))
        self._update_border_width()


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


    def element_at(self, x, y):
        alloc = self.get_allocation()
        if x < 0 or y < 0 or x > alloc.width or y > alloc.height:
            return None
        if self.element is None:
            return None
        x, y = self.translate_coordinates(self.element, x, y)
        return self.element.element_at(x, y)


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

gobject.type_register(Target)
