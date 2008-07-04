# -*- coding: UTF-8 -*-
# Copyright (C) 2006 Samuel Abels, http://debain.org
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
from Undoable import Undoable

class UndoText(Undoable):
    def __init__(self, action, start, end, text = None):
        Undoable.__init__(self)
        self.action = action
        self.start  = start
        self.end    = end
        self.text   = text

    def undo(self, buffer):
        if self.action == 'inserted':
            buffer.delete_range_at_offset(self.start, self.end)
        else:
            buffer.insert_at_offset(self.start, self.text)


    def redo(self, buffer):
        if self.action == 'inserted':
            buffer.insert_at_offset(self.start, self.text)
        else:
            buffer.delete_range_at_offset(self.start, self.end)
