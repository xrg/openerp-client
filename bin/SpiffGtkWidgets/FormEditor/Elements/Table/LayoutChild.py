# Copyright (C) 2009 Samuel Abels <http://debain.org>
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

class LayoutChild(object):
    left   = -1
    right  = -1
    top    = -1
    bottom = -1
    widget = None

    def __init__(self, widget):
        self.widget = widget


    def copy(self):
        child        = LayoutChild(self.widget.copy())
        child.left   = self.left
        child.right  = self.right
        child.top    = self.top
        child.bottom = self.bottom
        return child
