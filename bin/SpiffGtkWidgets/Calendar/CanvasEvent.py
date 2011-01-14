# -*- coding: utf-8 -*-
##############################################################################
# Copyright (C) 2008-2011 Samuel Abels
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License
# version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>
#
#
##############################################################################

import hippo
import gobject
from SpiffGtkWidgets import color
from CanvasRectangle import CanvasRectangle

class CanvasEvent(CanvasRectangle):
    """
    A canvas item representing a day.
    """
    def __init__(self, cal, event, **kwargs):
        """
        Constructor.
        """
        self.cal    = cal
        self.event  = event
        self.rulers = []
        CanvasRectangle.__init__(self, **kwargs)
        # Create canvas items.
        self.text = hippo.CanvasText(xalign    = hippo.ALIGNMENT_CENTER,
                                     yalign    = hippo.ALIGNMENT_CENTER,
                                     size_mode = hippo.CANVAS_SIZE_ELLIPSIZE_END)
        self.append(self.text, hippo.PACK_EXPAND)

    def set_text(self, text, description = ''):
        self.text.set_property('text', text + ', ' + description)


    def set_text_color(self, newcolor):
        self.text.props.color = color.to_int(newcolor)


    def set_text_properties(self, **kwargs):
        self.text.set_properties(**kwargs)


gobject.type_register(CanvasEvent)
