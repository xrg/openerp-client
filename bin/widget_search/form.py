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

import xml.dom.minidom
import pygtk
pygtk.require('2.0')
import gobject

from rpc import RPCProxy
import rpc

import gtk
from xml.parsers import expat

import sys
import wid_int
import tools

class _container(object):
    def __init__(self, max_width):
        self.cont = []
        self.max_width = max_width
        self.width = {}
        self.count = 0
        self.col=[]
    def new(self, col=8):
        self.col.append(col)
        table = gtk.Table(1, col)
        table.set_homogeneous(False)
        table.set_col_spacings(0)
        table.set_row_spacings(0)
        table.set_border_width(0)
        self.cont.append( (table, 1, 0) )
    def get(self):
        return self.cont[-1][0]
    def pop(self):
        (table, x, y) = self.cont.pop()
        self.col.pop()
        return table
    def newline(self):
        (table, x, y) = self.cont[-1]
        if x>0:
            self.cont[-1] = (table, 1, y+1)
        table.resize(y+1,self.col[-1])
        
    def wid_add(self, widget, colspan=1, name=None, expand=False, xoptions=False, ypadding=0, help=False, rowspan=1):

        self.count += 1
        (table, x, y) = self.cont[-1]
        if colspan>self.col[-1]:
            colspan=self.col[-1]
        if colspan+x>self.col[-1]:
            self.newline()
            (table, x, y) = self.cont[-1]
        if name:
            vbox = gtk.VBox(homogeneous=False, spacing=2)
            label = gtk.Label(name)
            label.set_alignment(0.0, 0.0)
            if help:
                try:
                    vbox.set_tooltip_markup('<span foreground=\"darkred\"><b>'+tools.to_xml(name)+'</b></span>\n'+tools.to_xml(help))
                except:
                    pass
                label.set_markup("<sup><span foreground=\"darkgreen\">?</span></sup>"+tools.to_xml(name))
            vbox.pack_start(label, expand=False)
            vbox.pack_start(widget, expand=expand, fill=False)
            wid = vbox
            wid.set_border_width(2)
        else:
            wid = widget
            if help:
                try:
                    wid.set_tooltip_markup('<span foreground=\"darkred\"></span>'+tools.to_xml(help))
                except:
                    pass
                    
        yopt = False
        if expand:
            yopt = yopt | gtk.EXPAND |gtk.FILL
        if not xoptions:
            xoptions = gtk.FILL|gtk.EXPAND    
        table.attach(wid, x, x+colspan, y, y+rowspan, yoptions=yopt, xoptions=xoptions, ypadding=ypadding, xpadding=0)
        self.cont[-1] = (table, x+colspan, y)
        wid_list = table.get_children()
        wid_list.reverse()
        table.set_focus_chain(wid_list)
        return wid

class parse(object):
    def __init__(self, parent, fields, model='', col=6):
        self.fields = fields
        self.name_lst = []
        self.name_lst1 = []
        dict_select = {'True':'1','False':'0','1':'1','0':'0'}
        import rpc
        all_field_ids =  rpc.session.rpc_exec_auth('/object', 'execute', 'ir.model.fields', 'search', [('model','=',str(model))])
        if len(fields) != len(all_field_ids):
            new_fields = []
            all_fields =  rpc.session.rpc_exec_auth('/object', 'execute', 'ir.model.fields', 'read', all_field_ids)
            for item in all_fields:
                if item['name'] not in fields:
                    new_fields.append(item)
            field_dict = {}
            for new_field in new_fields:
                if isinstance(new_field['select_level'],(str,unicode)):
                    new_field['select_level'] = eval(new_field['select_level'],dict_select)
                if isinstance(new_field['selectable'],(str,unicode)):
                    new_field['selectable'] = eval(new_field['selectable'],dict_select)    
                field_dict[new_field['name']]= {
                                                'string': new_field['field_description'],
                                                'type' : new_field['ttype'],
                                                'select': new_field['select_level'],
                                                'name' : new_field['name'],
                                                'readonly': new_field['readonly'],
                                                'relation': new_field['relation'],
                                                'required': new_field['required'],
                                                'translate': new_field['translate'],
                                                'selectable': new_field['selectable'],
                                                }
            self.fields.update(field_dict)    
            self.name_lst1=[('field',(field_dict[x])) for x in field_dict]
        
        self.parent = parent
        self.model = model
        self.col = col
        self.focusable = None
        self.add_widget_end = []

    def custom_remove(self, button, custom_panel):
        custom_panel.destroy()
        return True   

    def _psr_end(self, name):
        pass
    def _psr_char(self, char):
        pass

    def dummy_start(self,name,attrs):
            flag=False
            if name =='field' and attrs.has_key('name'):
                    for i in range (0,len(self.name_lst)):
                       if 'name' in self.name_lst[i][1]:
                           if self.name_lst[i][1]['name']==attrs['name']:
                               flag=True
                               if attrs.has_key('select'):
                                   self.name_lst[i]=(name,attrs)
                    if not flag:
                        self.name_lst.append((name,attrs))
            else:
                self.name_lst.append((name,attrs))

    def parse_filter(self, xml_data, max_width, root_node, call=None):
        psr = expat.ParserCreate()
        psr.StartElementHandler = self.dummy_start
        psr.EndElementHandler = self._psr_end
        psr.CharacterDataHandler = self._psr_char
        self.notebooks = []
        dict_widget = {}
        psr.Parse(xml_data)
        self.name_lst += self.name_lst1
        
        container = _container(max_width)
        attrs = tools.node_attributes(root_node)
        container.new(col=int(attrs.get('col', self.col)))
        self.container = container
        
        filter_hbox =  gtk.HBox(homogeneous=False, spacing=0)
        filter_button_exists = False
        
        for node in root_node.childNodes:
            if not node.nodeType==node.ELEMENT_NODE:
                continue
            attrs = tools.node_attributes(node)
            if node.localName=='field':
                val  = attrs.get('select', False) or self.fields[str(attrs['name'])].get('select', False)
                if val:
                    type = attrs.get('widget', self.fields[str(attrs['name'])]['type'])
                    
                    self.fields[str(attrs['name'])].update(attrs)
                    self.fields[str(attrs['name'])]['model']=self.model
                    if type not in widgets_type:
                        return False
                    widget_act = widgets_type[type][0](str(attrs['name']), self.parent, self.fields[attrs['name']])
                    if 'string' in self.fields[str(attrs['name'])]:
                        label = self.fields[str(attrs['name'])]['string']+' :'
                    else:
                        label = None
                    size = widgets_type[type][1]
                    if not self.focusable:
                        self.focusable = widget_act.widget
                    
                    mywidget = widget_act.widget
                    xoptions = 0
                    if node.childNodes:
                        mywidget = gtk.HBox(homogeneous=False, spacing=0)
                        mywidget.pack_start(widget_act.widget,expand=False,fill=False)
                        xoptions = gtk.SHRINK
                        i = 0           
                        for node_child in node.childNodes:
                            if node_child.localName == 'filter':
                                i += 1
                                attrs_child = tools.node_attributes(node_child)
                                widget_child = widgets_type['filter'][0]('', self.parent, attrs_child, call)
                                mywidget.pack_start(widget_child.widget)
                                dict_widget[str(attrs['name']) + str(i)] = (widget_child, mywidget, int(val))
                            elif node_child.localName == 'separator':
                                
                                attrs_child = tools.node_attributes(node_child)
                                if attrs_child.get('orientation','vertical') == 'horizontal':
                                    sep = gtk.HSeparator()
                                    sep.set_size_request(30,5)
                                    mywidget.pack_start(sep,False,True,5)
                                else:
                                    sep = gtk.VSeparator()
                                    sep.set_size_request(3,40)
                                    mywidget.pack_start(sep,False,False,5)
                                
#                        mywidget.pack_start(widget_act.widget,expand=False,fill=False)
                    wid = container.wid_add(mywidget, 1,label, int(self.fields[str(attrs['name'])].get('expand',0)),xoptions=xoptions)
                    dict_widget[str(attrs['name'])] = (widget_act, wid, int(val))
            
            elif node.localName == 'filter':
                name = str(attrs.get('string','filter'))
                widget_act = filter.filter(name, self.parent, attrs, call)
                wid = container.wid_add(widget_act.butt,xoptions=gtk.SHRINK, help=attrs.get('help',False))
                dict_widget[name]=(widget_act, widget_act, 1)
                
            elif node.localName == 'separator':
                
                if attrs.get('orientation','vertical') == 'horizontal':
                    sep_box = gtk.VBox(homogeneous=False, spacing=0)
                    sep = gtk.HSeparator()
                    sep.set_size_request(30,5)
                    sep_box.pack_start(gtk.Label(''),expand=False,fill=False)
                    sep_box.pack_start(sep,False,True,5)
                else:
                    sep_box = gtk.HBox(homogeneous=False, spacing=0)
                    sep = gtk.VSeparator()
                    sep.set_size_request(3,45)
                    sep_box.pack_start(sep,False,False,5)
                wid = container.wid_add(sep_box,xoptions=gtk.SHRINK)
                wid.show()
            elif node.localName=='newline':
                container.newline()

            elif node.localName=='group':
                if attrs.get('expand',False):
                    frame = gtk.Expander(attrs.get('string', None))
                else:
                    frame = gtk.Frame(attrs.get('string', None))
                    if not attrs.get('string', None):
                        frame.set_shadow_type(gtk.SHADOW_NONE)
                frame.attrs=attrs
                frame.set_border_width(0)

                container.wid_add(frame, colspan=int(attrs.get('colspan', 1)), expand=int(attrs.get('expand',0)), ypadding=0)
                container.new(int(attrs.get('col',8)))
                widget, widgets = self.parse_filter(xml_data, max_width, node, call= call)
                dict_widget.update(widgets)
                frame.add(self.widget)
                if not attrs.get('string', None):
                    container.get().set_border_width(0)
                container.pop()

#        if not flag:
#            
##Button for dynamic domain
#            flag = 1
#            img2 = gtk.Image()
#            img2.set_from_stock('gtk-add', gtk.ICON_SIZE_BUTTON)
#            self.button_dynamic = gtk.Button()
#            self.button_dynamic.set_image(img2)
#            self.button_dynamic.set_relief(gtk.RELIEF_NONE)
#            self.button_dynamic.set_alignment(0.3,0.3)
#                    
#            table = container.get()
#            table.attach(self.button_dynamic, 0, 1, 0, 1, yoptions=gtk.FILL, xoptions=gtk.FILL, ypadding=2, xpadding=0)
            
        self.widget = container.pop()
        self.container = container
        return self.widget, dict_widget

class form(wid_int.wid_int):
    def __init__(self, xml_arch, fields, model=None, parent=None, domain=[], call=None, col=6):
        wid_int.wid_int.__init__(self, 'Form', parent)
        parser = parse(parent, fields, model=model, col=col)
        self.parent = parent
        self.fields = fields
        self.model = model
        self.parser = parser
        self.call = call
        self.custom_widgets = {}
        #get the size of the window and the limite / decalage Hbox element
        ww, hw = 640,800
        if self.parent:
            ww, hw = self.parent.size_request()
        dom = xml.dom.minidom.parseString(xml_arch)
        
        self.widget, self.widgets = parser.parse_filter(xml_arch, ww, dom.firstChild, call=call)
        self.rows = 4
#        self.button_dynamic = parser.button_dynamic

#        fields_list = []
#        for k,v in self.fields.items():
#            if v['type'] in ('many2one','char','float','integer','date','datetime','selection','many2many','boolean'):
#                fields_list.append([k,v['string'],v['type']])
#        self.button_dynamic.connect('clicked', self.add_custom, self.widget, fields_list)
        self.focusable = parser.focusable
        self.id=None
        self.widget.show_all()
        self.name="" #parser.title
        self.show()
        value = {}
        for x in self.widgets.values():
            x[0].sig_activate(self.sig_activate)

    def clear(self, *args):
        for panel in self.custom_widgets:
            self.custom_widgets[panel][0].widget.destroy()
        self.custom_widgets = {}
        self.id = None
        for x in self.widgets.values():
            x[0].clear()
    
    def show(self):
        for w, widget, value in  self.widgets.values():
            if value >= 2:
                widget.show()
        self._hide=False

    def hide(self):
        for w, widget, value in  self.widgets.values():
            if value >= 2:
                widget.hide()
        self._hide=True
    
    def remove_custom(self, button, panel):
        button.parent.destroy()
        # Removing the Destroyed widget from Domain calculation
        for element in self.custom_widgets.keys():
            if self.custom_widgets[element][0] == panel:
                del self.custom_widgets[element]
                break
        return True 
    
    def add_custom(self, widget, table, fields):
        panel = widgets_type['custom_filter'][0]('', self.parent,{'fields':fields},call=self.remove_custom)
        x =  self.rows
        table.resize(x,4)
        table.attach(panel.widget,1, 4, x, x+1, yoptions=gtk.FILL, xoptions=gtk.FILL, ypadding=2, xpadding=0)
        panelx = 'panel' + str(x)
        self.custom_widgets[panelx] = (panel,table,1)
        self.rows +=1
        table.show()
        
        return panel
            
    def toggle(self, widget, event=None):
        pass

    def sig_activate(self, *args):
        if self.call:
            obj,fct = self.call
            fct(obj)

    def _value_get(self):
        domain = []
        context = {}
        for x in self.widgets.values() + self.custom_widgets.values():
            domain += x[0].value.get('domain',[])
            context.update( x[0].value.get('context',{}) )
            
        if domain:
            if len(domain)>1 and domain[-2] in ['&','|']:
                if len(domain) == 2:
                    domain = [domain[1]]
                else:
                    res1 = domain[:-2]
                    res2 = domain[-1:]
                    domain = res1 + res2
                                
        return {'domain':domain, 'context':context}

    def _value_set(self, value):
        for x in value:
            if x in self.widgets:
                self.widgets[x][0].value = value[x]
            if x in self.custom_widgets:
                self.custom_widgets[x][0].value = value[x]

    value = property(_value_get, _value_set, None, _('The content of the form or exception if not valid'))

import calendar
import spinbutton
import spinint
import selection
import char
import checkbox
import reference
import filter
import custom_filter

widgets_type = {
    'date': (calendar.calendar, 2),
    'datetime': (calendar.datetime, 2),
    'float': (spinbutton.spinbutton, 2),
    'float_time': (spinbutton.spinbutton, 2),
    'integer': (spinint.spinint, 2),
    'selection': (selection.selection, 2),
    'char': (char.char, 2),
    'boolean': (checkbox.checkbox, 2),
    'reference': (reference.reference, 2),
    'text': (char.char, 2),
    'text_wiki':(char.char, 2),
    'email': (char.char, 2),
    'url': (char.char, 2),
    'many2one': (char.char, 2),
    'one2many': (char.char, 2),
    'one2many_form': (char.char, 2),
    'one2many_list': (char.char, 2),
    'many2many_edit': (char.char, 2),
    'many2many': (char.char, 2),
    'callto': (char.char, 2),
    'sip': (char.char, 2),
    'filter' : (filter.filter,1),
    'custom_filter' : (custom_filter.custom_filter,6)
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
