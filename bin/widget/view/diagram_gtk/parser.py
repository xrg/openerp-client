# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from widget.view import interface
from tools import ustr, node_attributes
import gtk
import gtk.glade
import gettext
import common
from datetime import datetime, date
import rpc
from SpiffGtkWidgets import Calendar
from mx import DateTime
import time
import math
import xdot
import pydot # import pydot or you're not going to get anywhere my friend


class Viewdiagram(object):
    def __init__(self,window, model, node_attr, arrow_attr, attrs, screen):
        self.glade = gtk.glade.XML(common.terp_path("openerp.glade"),'widget_view_diagram', gettext.textdomain())
        self.widget = self.glade.get_widget('widget_view_diagram')
        self.model = model
        self.screen = screen
        self.node = node_attr
        self.arrow = arrow_attr
        self.id = screen.current_model.id
        self.window = xdot.DotWindow(window,self.widget, self.screen, node_attr, arrow_attr, attrs)
        self.draw_diagram()

    def draw_diagram(self):
        self.id = self.screen.current_model.id
        signal=self.arrow.get('signal',False)
        graph = pydot.Dot(graph_type='digraph')
        dict = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.ui.view', 'graph_get', self.id,self.model, self.node.get('object',False), self.arrow.get('object',False),self.arrow.get('source',False),self.arrow.get('destination',False),signal,(140, 180), rpc.session.context)
        node_lst = {}
        for node in dict['blank_nodes']:
            dict['nodes'][str(node['id'])] = {'name' : node['name']}
        for node in dict['nodes'].items():
            graph.add_node(pydot.Node(node[1]['name'],
                                      style="filled",
                                      shape=self.node.get('shape',''),
                                      color=self.node.get('bgcolor',''),
                                      URL=node[1]['name'] + "_" + node[0]  + "_node",
                                      ))
            node_lst[node[0]]  = node[1]['name']
        for edge in dict['transitions'].items():
            graph.add_edge(pydot.Edge(node_lst[str(edge[1][0])],
                                      node_lst[str(edge[1][1])],
                                      label=dict['signal'].get(edge[0],False)[1],
                                      URL = dict['signal'].get(edge[0],False)[1] + "_" + edge[0] + "_edge",
                                      fontsize='10',
                                      ))
        if not dict['nodes']:
            return True   
        file =  graph.create_xdot()
        self.window.set_dotcode(file, id = self.id)

    def display(self,screen, models):
        self.draw_diagram()
        pass

class parser_diagram(interface.parser_interface):
    def __init__(self, window, parent=None, attrs=None, screen=None):
           super(parser_diagram, self).__init__(window, parent=parent, attrs=attrs,
                    screen=screen)
           self.window = window
    def parse(self, model, root_node, fields):
        attrs = node_attributes(root_node)
        self.title = attrs.get('string', 'diagram')
        node_attr = None
        arrow_attr = None
        for node in root_node.childNodes:
            node_attrs = node_attributes(node)
            if node.localName == 'node':
                node_fields = []
                for child in node._get_childNodes():
                    if node_attributes(child) and node_attributes(child).get('name',False):
                        node_fields.append(node_attributes(child)['name'])
                fields = rpc.session.rpc_exec_auth('/object', 'execute', node_attrs.get('object',False), 'fields_get',node_fields)
                for key,val in fields.items():
                    fields[key]['name'] = key
                attrs['node'] = {'string' :node_attributes(root_node).get('string',False), 'views':{'form': {'fields': fields,'arch' : node.toxml('utf-8').replace('node','form')}}}
                node_attr = node_attrs
            if node.localName == 'arrow':
                arrow_fields = []
                for child in node._get_childNodes():
                    if node_attributes(child) and node_attributes(child).get('name',False):
                        arrow_fields.append(node_attributes(child)['name'])
                fields = rpc.session.rpc_exec_auth('/object', 'execute', node_attrs.get('object',False), 'fields_get',arrow_fields)
                for key,val in fields.items():
                    fields[key]['name'] = key
                attrs['arrow'] = {'string' :node_attributes(root_node).get('string',False), 'views':{'form': {'fields': fields,'arch' : node.toxml('utf-8').replace('arrow','form')}}}
                arrow_attr = node_attrs
        view = Viewdiagram(self.window, model, node_attr, arrow_attr, attrs,self.screen)
        return view, {}, [], ''

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

