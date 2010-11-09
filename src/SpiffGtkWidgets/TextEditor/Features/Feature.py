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

class Feature(object):
    """
    This class implements the common base class for all feature classes.
    """

    def __init__(self, buffer):
        """
        Constructor.
        
        buffer -- the associated TextBuffer
        """
        assert buffer is not None
        self.buffer = buffer


    def _print_range(self, start, end):
        print "RANGE:", repr(self.buffer.get_text(start, end))


    def _print_char(self, iter):
        end = iter.copy()
        end.forward_char()
        print "CHAR:", repr(self.buffer.get_text(iter, end))
