# Copyright (C) 2008-2011 Samuel Abels
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
import util

class Event(object):
    """
    This class represents an event that can be displayed in the calendar.
    """

    def __init__(self, caption, start, end = None, **kwargs):
        """
        Constructor.
        
        start -- datetime
        end -- datetime
        """
        assert caption is not None
        assert start   is not None
        self.id         = None
        self.caption    = caption
        self.start      = start
        self.end        = end
        self.all_day    = kwargs.get('all_day',    False)
        self.text_color = kwargs.get('text_color', None)
        self.bg_color   = kwargs.get('bg_color',   'orangered')
        if end is None:
            self.all_day = True
            self.end     = start
        if self.all_day:
            self.end = util.end_of_day(self.end)
