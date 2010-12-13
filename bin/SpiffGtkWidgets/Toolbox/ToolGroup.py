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

class ToolGroup(gtk.Expander):
    def __init__(self, name):
        gtk.Expander.__init__(self, name)
        self.buttons = []
        self.vbox    = gtk.VBox()
        self.add(self.vbox)
        self.set_expanded(True)


    def add_button(self, name, label):
        button = gtk.Button(label)
        button.set_name(name)
        button.set_alignment(0, 0)
        button.set_relief(gtk.RELIEF_NONE)
        self.vbox.pack_start(button)
        return button


    def add_icon_button(self, name, icon_file, label):
        icon   = gtk.image_new_from_file(icon_file)
        button = self.add_button(name, label)
        button.set_property('image', icon)
        return button

gobject.type_register(ToolGroup)
