# Copyright (C) 2009 Samuel Abels, http://debain.org
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
