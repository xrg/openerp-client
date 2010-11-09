# -*- coding: UTF-8 -*-
# Copyright (C) 2010 Samuel Abels
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
from Undoable import Undoable

class UndoCollection(Undoable):
    def __init__(self, buffer):
        Undoable.__init__(self, buffer, None)
        self.children = []


    def add(self, child):
        self.children.append(child)


    def undo(self):
        for child in reversed(self.children):
            child.undo()


    def redo(self):
        for child in self.children:
            child.redo()
