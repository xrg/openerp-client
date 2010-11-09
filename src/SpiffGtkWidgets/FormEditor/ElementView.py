# Copyright (C) 2009 Samuel Abels <http://debain.org>
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
import gobject, gtk, os.path
from SpiffGtkWidgets.Toolbox import Toolbox, ToolGroup
basedir = os.path.join(os.path.dirname(__file__))

class ElementView(Toolbox):
    def __init__(self, element_factory):
        Toolbox.__init__(self)
        self.factory = element_factory
        self.group   = ToolGroup('Elements')
        for element in element_factory.get_list():
            self.add_element(element)
        self.factory.connect('element-added', self._on_factory_element_added)
        self.add(self.group)


    def add_element(self, element):
        name    = element.name
        clsname = element.__module__.split('.')[-1]
        caption = element.caption
        icon    = os.path.join(basedir, 'Elements', clsname, 'icon.png')
        button  = self.group.add_icon_button(name, icon, caption)
        button.connect('button-press-event', self._on_button_press_event)


    def _on_factory_element_added(self, factory, element_class):
        self.add_element(element_class)


    def _on_button_press_event(self, button, event):
        self.emit('element-button-press-event', button, event)


gobject.signal_new('element-button-press-event',
                   ElementView,
                   gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT))

gobject.type_register(ElementView)
