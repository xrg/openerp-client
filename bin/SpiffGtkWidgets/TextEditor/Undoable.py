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

class Undoable(object):
    def __init__(self, buffer, startiter = None):
        self.buffer = buffer
        self.start  = None
        if startiter is not None:
            self.start = startiter.get_offset()


    def undo(self):
        raise Exception("Not implemented")


    def redo(self):
        raise Exception("Not implemented")
