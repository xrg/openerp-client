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
import pango, re
from Feature import Feature

bullet_point_re = re.compile(r'^(?:\d+\.|[\*\-])$')

class ListIndent(Feature):
    """
    This class implements an auto-indent feature for the text buffer.
    """

    def __init__(self, buffer):
        """
        Constructor.
        
        buffer -- the associated TextBuffer
        """
        Feature.__init__(self, buffer)
        self.bullet_point = u'•'
        self.first_li_tag = buffer.create_tag('first-list-item',
                                              left_margin = 30)
        self.li_tag       = buffer.create_tag('list-item',
                                              left_margin        = 30,
                                              pixels_above_lines = 12)
        self.bullet_tag   = buffer.create_tag('list-item-bullet',
                                              weight = pango.WEIGHT_ULTRABOLD)
        buffer.connect_after('insert-text', self._on_buffer_insert_text_after)


    def _at_bullet_point(self, iter):
        end = iter.copy()
        end.forward_find_char(lambda x, d: x == ' ')
        if end.is_end() or end.get_line() != iter.get_line():
            return False
        text = self.buffer.get_text(iter, end)
        if bullet_point_re.match(text):
            return True
        return False


    def _on_buffer_insert_text_after(self, buffer, iter, text, length):
        iter = iter.copy()
        iter.backward_chars(length)
        iter.set_line(iter.get_line())
        while not iter.is_end():
            if not self._at_bullet_point(iter):
                iter.forward_line()
                continue

            # Replace the item by a bullet point.
            end = iter.copy()
            end.forward_find_char(lambda x, d: x == ' ')
            buffer.delete(iter, end)
            buffer.insert(iter, self.bullet_point)
            iter.set_line(iter.get_line())

            # Markup the bullet point.
            end = iter.copy()
            end.forward_find_char(lambda x, d: x == ' ')
            buffer.apply_tag(self.bullet_tag, iter, end)

            # Markup the list item.
            end.forward_to_line_end()
            if iter.get_line() == 0:
                buffer.apply_tag(self.first_li_tag, iter, end)
            else:
                buffer.apply_tag(self.li_tag, iter, end)
            iter.forward_line()
