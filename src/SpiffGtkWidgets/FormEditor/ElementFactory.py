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
import gobject, gtk

class ElementFactory(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self.element_map  = {}
        self.element_list = []


    def register(self, element_class):
        self.element_map[element_class.name] = element_class
        self.element_list.append(element_class)
        self.emit('element-added', element_class)


    def create(self, name):
        return self.element_map[name]()


    def get_list(self, **kwargs):
        # kwargs.get('type') may be "layout widgets" or "buttons", for example
        return self.element_list


gobject.signal_new('element-added',
                   ElementFactory,
                   gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_PYOBJECT, ))

gobject.signal_new('element-removed',
                   ElementFactory,
                   gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_PYOBJECT, ))

gobject.type_register(ElementFactory)
