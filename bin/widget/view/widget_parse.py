# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import interface
import xml.dom.minidom

import form_gtk
import tree_gtk
import graph_gtk
import calendar_gtk

from form import ViewForm
from list import ViewList
from graph import ViewGraph
from calendar import ViewCalendar

parsers = {
    'form': form_gtk.parser_form,
    'tree': tree_gtk.parser_tree,
    'graph': graph_gtk.parser_graph,
    'calendar': calendar_gtk.parser_calendar,
}


parsers2 = {
    'form': ViewForm,
    'tree': ViewList,
    'graph': ViewGraph,
    'calendar': ViewCalendar,
}

class widget_parse(interface.parser_interface):
    def parse(self, screen, root_node, fields, toolbar={}):
        widget = None
        for node in root_node.childNodes:
            if not node.nodeType == node.ELEMENT_NODE:
                continue
            if node.localName in parsers:
                widget = parsers[node.localName](self.window, self.parent,
                        self.attrs, screen)
                wid, child, buttons, on_write = widget.parse(screen.resource,
                        node, fields)
                screen.set_on_write(on_write)
                res = parsers2[node.localName](self.window, screen, wid, child,
                        buttons, toolbar)
                res.title = widget.title
                widget = res
                break
            else:
                pass
        return widget


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

