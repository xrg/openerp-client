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
import gtk

class LayoutBox(object):
    annotation = None
    pull       = 0
    y          = 0
    height     = 0

    def __init__(self, parent, annotation):
        self.parent     = parent
        self.annotation = annotation
        self.annotation.connect('size-allocate', self._on_annotation_allocate)


    def _on_annotation_allocate(self, annotation, rect):
        self.height = rect.height
        self.parent.widget._update_annotations()
