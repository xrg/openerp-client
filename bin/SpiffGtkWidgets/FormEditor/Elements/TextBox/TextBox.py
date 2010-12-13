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
from gtk import gdk
from SpiffGtkWidgets.FormEditor.Elements import Element

class TextBox(Element):
    name     = 'textview'
    caption  = 'Text Box'
    xoptions = gtk.EXPAND|gtk.FILL
    yoptions = gtk.EXPAND|gtk.FILL

    def __init__(self, text = ''):
        Element.__init__(self, gtk.ScrolledWindow())
        self.textview = gtk.TextView()
        self.buffer   = self.textview.get_buffer()
        self.buffer.insert_at_cursor(text)
        self.child.set_shadow_type(gtk.SHADOW_IN)
        self.child.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.child.add(self.textview)


    def copy(self):
        return TextBox(self.get_text())


    def get_text(self):
        return self.buffer.get_text(*self.buffer.get_bounds())

gobject.type_register(TextBox)
