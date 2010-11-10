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

class OptionBox(Element):
    name     = 'optionmenu'
    caption  = 'Option Box'
    xoptions = gtk.EXPAND|gtk.FILL
    yoptions = gtk.FILL

    def __init__(self, options = None):
        Element.__init__(self, gtk.ComboBox())
        self.options = []
        for option in options or []:
            self.add_option(option)


    def copy(self):
        return OptionBox(self.options)


    def add_option(self, option):
        self.options.append(option)
        self.child.append_text(gtk.MenuItem(option))


    def get_options(self):
        return self.options

gobject.type_register(OptionBox)
