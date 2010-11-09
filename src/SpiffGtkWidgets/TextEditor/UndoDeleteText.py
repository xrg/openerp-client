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

class UndoDeleteText(Undoable):
    def __init__(self, buffer, startiter, enditer):
        Undoable.__init__(self, buffer, startiter)
        self.end  = enditer.get_offset()
        self.tags = buffer.get_tags_at_offset(self.start, self.end)
        self.text = buffer.get_text(startiter, enditer)


    def undo(self):
        self.buffer.insert_at_offset(self.start, self.text)
        self.buffer.apply_tags_at_offset(self.tags, self.start, self.end)


    def redo(self):
        self.buffer.delete_range_at_offset(self.start, self.end)
