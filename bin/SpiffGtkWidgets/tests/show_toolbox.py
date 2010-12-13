# -*- coding: UTF-8 -*-
# Copyright (C) 2008 Samuel Abels, http://debain.org
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
import sys, os.path, gtk
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from SpiffGtkWidgets.Toolbox import Toolbox, ToolGroup
import SpiffGtkWidgets.FormEditor
form_editor_dir = os.path.dirname(SpiffGtkWidgets.FormEditor.__file__)
icon_dir        = os.path.join(form_editor_dir, 'icons')

class Window(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        toolbox = Toolbox()
        toolbox.connect('button-clicked', self._on_button_clicked)

        # Add first group without icons.
        group = ToolGroup('My ToolGroup')
        group.add_button('button1', 'Button 1')
        group.add_button('button2', 'Button 2')
        toolbox.add(group)

        # Add another group with icons.
        group = ToolGroup('My ToolGroup')
        icon1 = os.path.join(icon_dir, 'label.png')
        icon2 = os.path.join(icon_dir, 'table.png')
        group.add_icon_button('button3', icon1, 'Button 3')
        group.add_icon_button('button4', icon2, 'Button 4')
        toolbox.add(group)

        self.add(toolbox)
        self.show_all()


    def _on_button_clicked(self, toolbox, button):
        print "Clicked:", button.get_name()


# Create widgets.
window = Window()
window.connect('delete-event', gtk.main_quit)
gtk.main()
