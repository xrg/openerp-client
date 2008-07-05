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
from Undoable import Undoable

class UndoTag(Undoable):
    def __init__(self, action, startiter, enditer, tag, buffer):
        Undoable.__init__(self)
        self.action   = action
        self.start    = startiter.get_offset()
        self.end      = enditer.get_offset()
        self.old_tags = self._get_tags(buffer)
        self.tag      = tag


    def _get_tags(self, buffer):
        taglist = []
        iter    = buffer.get_iter_at_offset(self.start)
        while True:
            taglist.append(iter.get_tags())
            iter.forward_char()
            if iter.get_offset() >= self.end:
                break
        return taglist


    def _apply_tags(self, buffer, taglist):
        start = buffer.get_iter_at_offset(self.start)
        end   = buffer.get_iter_at_offset(self.start + 1)
        for tags in taglist:
            for tag in tags:
                buffer.apply_tag(tag, start, end)
            start.forward_char()
            end.forward_char()


    def undo(self, buffer):
        if self.action == 'applied':
            buffer.remove_tag_at_offset(self.tag, self.start, self.end)
            self._apply_tags(buffer, self.old_tags)
        else:
            self._apply_tags(buffer, self.old_tags)


    def redo(self, buffer):
        if self.action == 'applied':
            buffer.apply_tag_at_offset(self.tag, self.start, self.end)
        else:
            buffer.remove_tag_at_offset(self.tag, self.start, self.end)
