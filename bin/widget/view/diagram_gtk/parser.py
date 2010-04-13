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
from tools import node_attributes
import gtk
import gtk.glade
import gettext
import common
import rpc
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
        self.id = None
        if self.screen.current_model:
            self.id = screen.current_model.id 
        self.window = xdot.DotWindow(window,self.widget, self.screen, node_attr, arrow_attr, attrs)
        self.draw_diagram()

    def draw_diagram(self):
        if self.screen.current_model:
            self.id = self.screen.current_model.id 
        signal=self.arrow.get('signal',False)
        graph = pydot.Dot(graph_type='digraph')

        if self.id:
            dict = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.ui.view', 'graph_get', self.id, self.model, self.node.get('object',False), self.arrow.get('object',False),self.arrow.get('source',False),self.arrow.get('destination',False),signal,(140, 180), rpc.session.context)
            node_lst = {}
            for node in dict['blank_nodes']:
                dict['nodes'][str(node['id'])] = {'name' : node['name']}

            record_list = rpc.session.rpc_exec_auth('/object', 'execute', self.node.get('object',False), 'read', dict['nodes'].keys())
            shapes = {}
            for shape_field in self.node.get('shape','').split(';'):
                if shape_field:
                    shape, field = shape_field.split(':')
                    shapes[shape] = field
            for record in record_list:
                record['shape'] = 'ellipse'     
                for shape, expr in shapes.items():
                    if eval(expr, record):
                        record['shape'] = shape 

            for node in dict['nodes'].items():
                record = {}
                for res in record_list:
                    if int(node[0]) == int(res['id']):
                        record = res
                        break

                graph.add_node(pydot.Node(node[1]['name'],
                                          style="filled",
                                          shape=record['shape'],
                                          color=self.node.get('bgcolor',''),
                                          URL=node[1]['name'] + "_" + node[0]  + "_node",
                                          ))
                node_lst[node[0]]  = node[1]['name']
            for edge in dict['transitions'].items():
                if len(edge) < 1 or str(edge[1][0]) not in node_lst or str(edge[1][1]) not in node_lst:
                    continue
                graph.add_edge(pydot.Edge(node_lst[str(edge[1][0])],
                                          node_lst[str(edge[1][1])],
                                          label=dict['signal'].get(edge[0],False)[1],
                                          URL = dict['signal'].get(edge[0],False)[1] + "_" + edge[0] + "_edge",
                                          fontsize='10',
                                          ))
            file =  graph.create_xdot()
            if not dict['nodes']:
                file = """digraph G {}"""
            self.window.set_dotcode(file, id=self.id, graph=graph)

    def display(self):
        self.draw_diagram()
        return False

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
                node_attr = node_attrs
            if node.localName == 'arrow':
                arrow_attr = node_attrs
        if node_attr.get('form_view_ref',False):
            view_id = rpc.session.rpc_exec_auth('/object', 'execute', "ir.model.data", 'search' ,[('name','=', node_attr.get('form_view_ref',''))])
            view_id = rpc.session.rpc_exec_auth('/object', 'execute', "ir.model.data", 'read' ,view_id, ['res_id'])
            print "view_id and view_id[0]['res_id']:",view_id and view_id[0]['res_id']
            node_attr['form_view_ref'] = view_id and view_id[0]['res_id']
        else:
            node_attr['form_view_ref'] = False
        if arrow_attr.get('form_view_ref',False):
            view_id = rpc.session.rpc_exec_auth('/object', 'execute', "ir.model.data", 'search' ,[('name','=', arrow_attr.get('form_view_ref',''))])
            view_id = rpc.session.rpc_exec_auth('/object', 'execute', "ir.model.data", 'read' ,view_id, ['res_id'])
            arrow_attr['form_view_ref'] = view_id and view_id[0]['res_id']
        else:
            arrow_attr['form_view_ref'] = False
        view = Viewdiagram(self.window, model, node_attr, arrow_attr, attrs,self.screen)
        return view, {}, [], ''
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

