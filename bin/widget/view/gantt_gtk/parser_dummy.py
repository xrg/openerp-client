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

from widget.view import interface
import tools
import gtk


class EmptyGantt(object):
    def __init__(self, model):
        self.widget = gtk.Label(
            _('Gantt View Error !')+'\n\n'+
            _('Gantt not implemented in GTK Client, please use the Web Client.'))

    def display(self, models):
        pass


class parser_gantt(interface.parser_interface):
    def parse(self, model, root_node, fields):
        attrs = tools.node_attributes(root_node)
        self.title = attrs.get('string', 'Unknown')

        on_write = ''

        view = EmptyGantt(model)

        return view, {}, [], on_write

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

