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
