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
import gobject, gtk, pango
from Element import Element

class Button(Element):
    name     = 'button'
    caption  = 'Button'
    xoptions = gtk.FILL
    yoptions = gtk.FILL

    def __init__(self, *args):
        Element.__init__(self, gtk.Button(*args))
        self.set_above_child(True)
        if len(args) == 0:
            self.child.set_label('Button')
