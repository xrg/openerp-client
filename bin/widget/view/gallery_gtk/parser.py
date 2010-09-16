# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

import gtk
import tools

from widget.view import interface

class EmptyGallery(object):
    def __init__(self, model, fields, attrs, gallery_fields):
        self.widget = gtk.Image()

    def display(self, models):
        pass

class parser_gallery(interface.parser_interface):
    def parse(self, model, root_node, fields):
        attrs = tools.node_attributes(root_node)
        self.title = attrs.get('string', 'Unknown')

        on_write = '' #attrs.get('on_write', '')

        gallery_fields = {
            'image': False,
            'text': False,
        }
        for node in root_node:
            node_attrs = tools.node_attributes(node)
            if node.tag == 'field':
                node_type = node_attrs.get('type', '')
                if node_type in gallery_fields:
                    gallery_fields[node_type] = node_attrs.get('name', False)

        try:
            import gallery
            view = gallery.ViewGallery(model, fields, attrs, gallery_fields)
        except Exception:
            import common
            import traceback
            import sys
            tb_s = reduce(lambda x, y: x + y, traceback.format_exception(
                sys.exc_type, sys.exc_value, sys.exc_traceback))
            common.error('Gallery', _('Can not generate galllery !'), details=tb_s,
                    parent=self.window)
            view = EmptyGallery(model, fields, attrs, gallery_fields)
        return view, {}, [], on_write




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

