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
from gtk import gdk
from Element import Element

class EntryBox(Element):
    name     = 'entry'
    caption  = 'Entry Box'
    xoptions = gtk.EXPAND|gtk.FILL
    yoptions = gtk.FILL

    def __init__(self, text = ''):
        Element.__init__(self, gtk.Entry())
        self.child.set_text(text)
        #self.connect('button-press-event', self._on_button_press_event)


    def copy(self):
        return EntryBox(self.child.get_text())


    def _on_button_press_event(self, evbox, event):
        print "Pressed", event.x, event.y
        entry = self.child
        alloc = entry.get_allocation()
        pad   = 10
        if event.x < pad or event.x > alloc.width - pad:
            return False
        if event.y < pad or event.y > alloc.height - pad:
            return False
        entry.grab_focus()
        return True

gobject.type_register(EntryBox)
