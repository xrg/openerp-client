# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from rpc import RPCProxy
import rpc
import gettext

import gtk
import gobject
from gtk import glade

from widget.model.group import ModelRecordGroup

from widget.view.screen_container import screen_container
import widget_search

import signal_event
import tools
import service
import common


class Screen(signal_event.signal_event):

    def __init__(self, model_name, view_ids=None, view_type=None,
            parent=None, context=None, views_preload=None, tree_saves=True,
            domain=None, create_new=False, row_activate=None, hastoolbar=False,
            hassubmenu=False,default_get=None, show_search=False, window=None,
            limit=80, readonly=False, is_wizard=False, search_view=None):
        if view_ids is None:
            view_ids = []
        if view_type is None:
            view_type = ['tree', 'form']
        if context is None:
            context = {}
        if views_preload is None:
            views_preload = {}
        if domain is None:
            domain = []
        if default_get is None:
            default_get = {}
        if search_view is None:
            search_view = "{}"            

        super(Screen, self).__init__()

        self.show_search = show_search
        self.search_count = 0
        self.hastoolbar = hastoolbar
        self.hassubmenu = hassubmenu        
        self.default_get=default_get
        if not row_activate:
            self.row_activate = lambda self,screen=None: self.switch_view(screen, 'form')
        else:
            self.row_activate = row_activate
        self.create_new = create_new
        self.name = model_name
        self.domain = domain
        self.latest_search = []
        self.views_preload = views_preload
        self.resource = model_name
        self.rpc = RPCProxy(model_name)
        self.context = context
        self.context.update(rpc.session.context)
        self.views = []
        self.fields = {}
        self.view_ids = view_ids
        self.models = None
        self.parent=parent
        self.window=window
        self.is_wizard = is_wizard
        self.search_view = eval(search_view)
        models = ModelRecordGroup(model_name, self.fields, parent=self.parent, context=self.context, is_wizard=is_wizard)
        self.models_set(models)
        self.current_model = None
        self.screen_container = screen_container()
        self.filter_widget = None
        self.widget = self.screen_container.widget_get()
        self.__current_view = 0
        self.tree_saves = tree_saves
        self.limit = limit
        self.old_limit = limit
        self.offset = 0        
        self.readonly= readonly
        self.action_domain = []
        self.custom_panels = []        

        if view_type:
            self.view_to_load = view_type[1:]
            view_id = False
            if view_ids:
                view_id = view_ids.pop(0)
            view = self.add_view_id(view_id, view_type[0])
            self.screen_container.set(view.widget)
        self.display()


    def readonly_get(self):
        return self._readonly

    def readonly_set(self, value):
        self._readonly = value
        self.models._readonly = value

    readonly = property(readonly_get, readonly_set)

    def search_active(self, active=True, show_search=True):

        if active:
            if not self.filter_widget:
                if not self.search_view:
                    self.search_view = rpc.session.rpc_exec_auth('/object', 'execute',
                            self.name, 'fields_view_get', False, 'form',
                            self.context)
                self.filter_widget = widget_search.form(self.search_view['arch'],
                        self.search_view['fields'], self.name, self.window,
                        self.domain, (self, self.search_filter))
                self.search_count = rpc.session.rpc_exec_auth_try('/object', 'execute', self.name, 'search_count', [], self.context)                
                self.screen_container.add_filter(self.filter_widget.widget,
                        self.search_filter, self.search_clear,
                        self.search_offset_next,
                        self.search_offset_previous, self.search_count, 
                        self.execute_action, self.add_custom, self.name)
                
        if active and show_search:
            self.screen_container.show_filter()
        else:
            self.screen_container.hide_filter()

    def update_scroll(self, *args):
        offset=self.offset
        limit = self.screen_container.get_limit()
        if offset<=0:
            self.screen_container.but_previous.set_sensitive(False)
        else:
            self.screen_container.but_previous.set_sensitive(True)

        if offset+limit>=self.search_count:
            self.screen_container.but_next.set_sensitive(False)
        else:
            self.screen_container.but_next.set_sensitive(True)

    def search_offset_next(self, *args):
        offset=self.offset
        limit = self.screen_container.get_limit()
        self.offset = offset+limit
        self.search_filter()

    def search_offset_previous(self, *args):
        offset=self.offset
        limit = self.screen_container.get_limit()
        self.offset = max(offset-limit,0)
        self.search_filter()

    def search_clear(self, *args):
        self.filter_widget.clear()
        self.screen_container.action_combo.set_active(0)        
        self.clear()

    def search_filter(self, *args):
        v = self.filter_widget and self.filter_widget.value or []
        v = self.action_domain and  (v + self.action_domain) or v
        filter_keys = []

        for ele in v:
            if isinstance(ele,tuple):
                filter_keys.append(ele[0])

        for element in self.domain:
            if not isinstance(element,tuple): # Filtering '|' symbol
                v.append(element)
            else:
                (key, op, value) = element
                if key not in filter_keys and not (key=='active' and self.context.get('active_test', False)):
                    v.append((key, op, value))

#        v.extend((key, op, value) for key, op, value in domain if key not in filter_keys and not (key=='active' and self.context.get('active_test', False)))
        if self.latest_search != v:
            self.offset = 0
        limit=self.screen_container.get_limit()
        offset=self.offset
        self.latest_search = v
        ids = rpc.session.rpc_exec_auth('/object', 'execute', self.name, 'search', v, offset, limit, 0, self.context)
        if len(ids) < limit:
            self.search_count = len(ids)
        else:
            self.search_count = rpc.session.rpc_exec_auth_try('/object', 'execute', self.name, 'search_count', v, self.context)

        self.update_scroll()

        self.clear()
        self.load(ids)
        return True

    def add_custom(self, dynamic_button):
        fields_list = []
        for k,v in self.search_view['fields'].items():
            if v['type'] in ('many2one','char','float','integer','date','datetime','selection','many2many','boolean','one2many') and v.get('selectable', False):
                fields_list.append([k,v['string'],v['type']])
        if fields_list:
            fields_list.sort(lambda x, y: cmp(x[1], y[1]))
        panel = self.filter_widget.add_custom(self.filter_widget, self.filter_widget.widget, fields_list)
        self.custom_panels.append(panel)

        if len(self.custom_panels)>1:
            self.custom_panels[-1].condition_next.hide()
            self.custom_panels[-2].condition_next.show()

    def execute_action(self, combo):
        flag = combo.get_active_text()
        self.action_domain = []

        # 'mf' Section manages Filters
        if flag == 'mf':
            obj = service.LocalService('action.main')
            act={'name':'Manage Filters',
                 'res_model':'ir.actions.act_window',
                 'type':'ir.actions.act_window',
                 'view_type':'form',
                 'view_mode':'tree,form',
                 'domain':'[(\'filter\',\'=\',True),(\'res_model\',\'=\',\''+self.name+'\'),(\'default_user_ids\',\'in\',(\''+str(rpc.session.uid)+'\',))]'}
            value = obj._exec_action(act, {}, self.context)

        if flag in ['blk','mf']:
            self.search_filter()
            combo.set_active(0)
            return True
        #This section handles shortcut and action creation
        elif flag in ['sh','sf']:
            glade2 = glade.XML(common.terp_path("openerp.glade"),'dia_get_action',gettext.textdomain())
            widget = glade2.get_widget('action_name')
            win = glade2.get_widget('dia_get_action')
            form_combo = glade2.get_widget('combo_form')
            tree_combo = glade2.get_widget('combo_tree')
            graph_combo = glade2.get_widget('combo_graph')
            calendar_combo = glade2.get_widget('combo_calendar')
            gantt_combo = glade2.get_widget('combo_gantt')
            win.set_icon(common.OPENERP_ICON)
            if flag == 'sh':
                win.set_title('Shortcut Entry')
                lbl = glade2.get_widget('label157')
                lbl.set_text('Enter Shortcut Name:')
            
            new_view_ids = rpc.session.rpc_exec_auth_try('/object', 'execute', 'ir.ui.view', 'search', [('model','=',self.resource),('inherit_id','=',False)])
            view_datas = rpc.session.rpc_exec_auth_try('/object', 'execute', 'ir.ui.view', 'read', new_view_ids, ['id','name','type'])
            cell = gtk.CellRendererText()
            liststore_form = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
            form_combo.set_model(liststore_form)
            form_combo.pack_start(cell, True)
            form_combo.add_attribute(cell, 'text', 1)
                        
            liststore_tree = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
            tree_combo.set_model(liststore_tree)
            tree_combo.pack_start(cell, True)
            tree_combo.add_attribute(cell, 'text', 1)
                        
            liststore_graph = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
            graph_combo.set_model(liststore_graph)
            graph_combo.pack_start(cell, True)
            graph_combo.add_attribute(cell, 'text', 1)
                                
            liststore_calendar = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
            calendar_combo.set_model(liststore_calendar)
            calendar_combo.pack_start(cell, True)
            calendar_combo.add_attribute(cell, 'text', 1)
                        
            liststore_gantt = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
            gantt_combo.set_model(liststore_gantt)
            gantt_combo.pack_start(cell, True)
            gantt_combo.add_attribute(cell, 'text', 1)
            
            for data in view_datas:
                if data['type'] == 'form':
                    liststore_form.append([data['id'],data['name']])
                elif data['type'] == 'tree':
                    liststore_tree.append([data['id'],data['name']])
                elif data['type'] == 'graph':
                    liststore_graph.append([data['id'],data['name']])
                elif data['type'] == 'calendar':
                    liststore_calendar.append([data['id'],data['name']])
                elif data['type'] == 'gantt':
                    liststore_gantt.append([data['id'],data['name']])
            form_combo.set_active(0)
            tree_combo.set_active(0)
            graph_combo.set_active(0)
            calendar_combo.set_active(0)
            gantt_combo.set_active(0)                
            win.show_all()
            response = win.run()
            win.destroy()
            combo.set_active(0)
            if response == gtk.RESPONSE_OK and widget.get_text():
                action_name = widget.get_text()
                v_ids=[]                
                if form_combo.get_active_text():
                    rec = {'view_mode':'form', 'view_id':form_combo.get_active_text(), 'sequence':2}
                    v_ids.append(rpc.session.rpc_exec_auth('/object', 'execute', 'ir.actions.act_window.view', 'create', rec))
                if tree_combo.get_active_text():
                    rec = {'view_mode':'tree', 'view_id':tree_combo.get_active_text(), 'sequence':1}
                    v_ids.append(rpc.session.rpc_exec_auth('/object', 'execute', 'ir.actions.act_window.view', 'create', rec))
                if graph_combo.get_active_text():
                    rec = {'view_mode':'graph', 'view_id':graph_combo.get_active_text(), 'sequence':4}
                    v_ids.append(rpc.session.rpc_exec_auth('/object', 'execute', 'ir.actions.act_window.view', 'create', rec))
                if calendar_combo.get_active_text():
                    rec = {'view_mode':'calendar', 'view_id':calendar_combo.get_active_text(), 'sequence':3}
                    v_ids.append(rpc.session.rpc_exec_auth('/object', 'execute', 'ir.actions.act_window.view', 'create', rec))
                if gantt_combo.get_active_text():
                    rec = {'view_mode':'gantt', 'view_id':gantt_combo.get_active_text(), 'sequence':5}                                        
                    v_ids.append(rpc.session.rpc_exec_auth('/object', 'execute', 'ir.actions.act_window.view', 'create', rec))

                datas={'name':action_name,
                       'res_model':self.name,
                       'domain':str(self.filter_widget and self.filter_widget.value),
                       'context':str({}),
                       'view_ids':[(6,0,v_ids)],
                       'search_view_id':self.search_view['view_id'],
                       'filter':True,
                       'default_user_ids': [[6, 0, [rpc.session.uid]]],
                       }
                action_id = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.actions.act_window', 'create', datas)
                self.screen_container.fill_filter_combo(self.name)
                if flag == 'sh':
                    parent_menu_id = rpc.session.rpc_exec_auth_try('/object', 'execute', 'ir.ui.menu', 'search', [('name','=','Custom Shortcuts')])
                    if parent_menu_id:
                        menu_data={'name':action_name,
                                   'sequence':20,
                                   'action':'ir.actions.act_window,'+str(action_id),
                                   'parent_id':parent_menu_id[0],
                                   'icon':'STOCK_JUSTIFY_FILL',
                                   }
                        menu_id = rpc.session.rpc_exec_auth_try('/object', 'execute', 'ir.ui.menu', 'create', menu_data)
                        sc_data={'name':action_name,
                                 'sequence': 1,
                                 'res_id': menu_id,
                                   }
                        shortcut_id = rpc.session.rpc_exec_auth_try('/object', 'execute', 'ir.ui.view_sc', 'create', sc_data)
                return True
        else:
            try:
                self.action_domain = flag and tools.expr_eval(flag) or []
                if isinstance(self.action_domain,type([])):
                    self.search_filter()
            except Exception, e:
                return True
#        self.action_domain=[]
#        combo.set_active(0)

    def models_set(self, models):
        import time
        c = time.time()
        if self.models:
            self.models.signal_unconnect(self.models)
        self.models = models
        self.parent = models.parent
        if len(models.models):
            self.current_model = models.models[0]
        else:
            self.current_model = None
        self.models.signal_connect(self, 'record-cleared', self._record_cleared)
        self.models.signal_connect(self, 'record-changed', self._record_changed)
        self.models.signal_connect(self, 'model-changed', self._model_changed)
        models.add_fields(self.fields, models)
        self.fields.update(models.fields)
        models.is_wizard = self.is_wizard

    def _record_cleared(self, model_group, signal, *args):
        for view in self.views:
            view.reload = True

    def _record_changed(self, model_group, signal, *args):
        for view in self.views:
            view.signal_record_changed(signal[0], model_group.models, signal[1], *args)

    def _model_changed(self, model_group, model):
        if (not model) or (model==self.current_model):
            self.display()

    def _get_current_model(self):
        return self.__current_model

    #
    # Check more or less fields than in the screen !
    #
    def _set_current_model(self, value):
        self.__current_model = value
        try:
            offset = int(self.offset)
        except:
            offset = 0
        try:
            pos = self.models.models.index(value)
        except:
            pos = -1
        self.signal('record-message', (pos + offset,
            len(self.models.models or []) + offset,
            self.search_count,
            value and value.id))
        return True
    current_model = property(_get_current_model, _set_current_model)

    def destroy(self):
        for view in self.views:
            view.destroy()
            del view
        #del self.current_model
        self.models.signal_unconnect(self)
        del self.models
        del self.views

    # mode: False = next view, value = open this view
    def switch_view(self, screen=None, mode=False):
        self.current_view.set_value()
        if self.current_model and self.current_model not in self.models.models:
            self.current_model = None
        if mode:
            ok = False
            for vid in range(len(self.views)):
                if self.views[vid].view_type==mode:
                    self.__current_view = vid
                    ok = True
                    break
            while not ok and len(self.view_to_load):
                self.load_view_to_load()
                if self.current_view.view_type==mode:
                    ok = True
            for vid in range(len(self.views)):
                if self.views[vid].view_type==mode:
                    self.__current_view = vid
                    ok = True
                    break
            if not ok:
                self.__current_view = len(self.views) - 1
        else:
            if len(self.view_to_load):
                self.load_view_to_load()
                self.__current_view = len(self.views) - 1
            else:
                self.__current_view = (self.__current_view + 1) % len(self.views)
        widget = self.current_view.widget
        self.screen_container.set(self.current_view.widget)
        if self.current_model:
            self.current_model.validate_set()
        elif self.current_view.view_type=='form':
            self.new()
        self.display()
        self.current_view.set_cursor()

        main = service.LocalService('gui.main')
        if main:
            main.sb_set()

        # TODO: set True or False accoring to the type

    def load_view_to_load(self, mode=False):
        if len(self.view_to_load):
            if self.view_ids:
                view_id = self.view_ids.pop(0)
                view_type = self.view_to_load.pop(0)
            else:
                view_id = False
                view_type = self.view_to_load.pop(0)
            self.add_view_id(view_id, view_type)

    def add_view_custom(self, arch, fields, display=False, toolbar={}, submenu={}):
        return self.add_view(arch, fields, display, True, toolbar=toolbar, submenu=submenu)

    def add_view_id(self, view_id, view_type, display=False, context=None):
        if view_type in self.views_preload:
            return self.add_view(self.views_preload[view_type]['arch'],
                    self.views_preload[view_type]['fields'], display,
                    toolbar=self.views_preload[view_type].get('toolbar', False),
                    submenu=self.views_preload[view_type].get('submenu', False),
                    context=context)
        else:
            view = self.rpc.fields_view_get(view_id, view_type, self.context,
                    self.hastoolbar, self.hassubmenu)
            return self.add_view(view['arch'], view['fields'], display,
                    toolbar=view.get('toolbar', False), submenu=view.get('submenu', False), context=context)

    def add_view(self, arch, fields, display=False, custom=False, toolbar=None, submenu=None,
            context=None):
        if toolbar is None:
            toolbar = {}
        if submenu is None:
            submenu = {}            
        def _parse_fields(node, fields):
            if node.nodeType == node.ELEMENT_NODE:
                if node.localName=='field':
                    attrs = tools.node_attributes(node)
                    if attrs.get('widget', False):
                        if attrs['widget']=='one2many_list':
                            attrs['widget']='one2many'
                        attrs['type'] = attrs['widget']
                    fields[str(attrs['name'])].update(attrs)
            for node2 in node.childNodes:
                _parse_fields(node2, fields)
        dom = xml.dom.minidom.parseString(arch)
        _parse_fields(dom, fields)
        for dom in self.domain:
            if dom[0] in fields:
                field_dom = str(fields[dom[0]].setdefault('domain',
                        []))
                fields[dom[0]]['domain'] = field_dom[:1] + \
                        str(('id', dom[1], dom[2])) + ',' + field_dom[1:]

        from widget.view.widget_parse import widget_parse
        models = self.models.models
        if self.current_model and (self.current_model not in models):
            models = models + [self.current_model]
        if custom:
            self.models.add_fields_custom(fields, self.models)
        else:
            self.models.add_fields(fields, self.models, context=context)
        self.fields = self.models.fields

        parser = widget_parse(parent=self.parent, window=self.window)
        dom = xml.dom.minidom.parseString(arch)
        view = parser.parse(self, dom, self.fields, toolbar=toolbar, submenu=submenu)
        if view:
            self.views.append(view)

        if display:
            self.__current_view = len(self.views) - 1
            self.current_view.display()
            self.screen_container.set(view.widget)
        return view

    def editable_get(self):
        if hasattr(self.current_view, 'widget_tree'):
            return self.current_view.widget_tree.editable
        else:
            return False

    def new(self, default=True, context={}):
        if self.current_view and self.current_view.view_type == 'tree' \
                and not self.current_view.widget_tree.editable:
            self.switch_view(mode='form')
        ctx = self.context.copy()
        ctx.update(context)
        model = self.models.model_new(default, self.domain, ctx)
        if (not self.current_view) or self.current_view.model_add_new or self.create_new:
            self.models.model_add(model, self.new_model_position())
        self.current_model = model
        self.current_model.validate_set()
        self.display()
        if self.current_view:
            self.current_view.set_cursor(new=True)
        return self.current_model

    def new_model_position(self):
        position = -1
        if self.current_view and self.current_view.view_type =='tree' \
                and self.current_view.widget_tree.editable == 'top':
            position = 0
        return position

    def set_on_write(self, func_name):
        self.models.on_write = func_name

    def cancel_current(self):
        if self.current_model:
            self.current_model.cancel()
        if self.current_view:
            self.current_view.cancel()

    def save_current(self):
        if not self.current_model:
            return False
        self.current_view.set_value()
        id = False
        if self.current_model.validate():
            id = self.current_model.save(reload=True)
            self.models.writen(id)
            if not id:
                self.current_view.display()
        else:
            self.current_view.display()
            self.current_view.set_cursor()
            return False
        if self.current_view.view_type == 'tree':
            for model in self.models.models:
                if model.is_modified():
                    if model.validate():
                        id = model.save(reload=True)
                        self.models.writen(id)
                    else:
                        self.current_model = model
                        self.display()
                        self.current_view.set_cursor()
                        return False
            self.display()
            self.current_view.set_cursor()
        if self.current_model not in self.models:
            self.models.model_add(self.current_model)
        return id

    def _getCurrentView(self):
        if not len(self.views):
            return None
        return self.views[self.__current_view]
    current_view = property(_getCurrentView)

    def get(self):
        if not self.current_model:
            return None
        self.current_view.set_value()
        return self.current_model.get()

    def is_modified(self):
        if not self.current_model:
            return False
        self.current_view.set_value()
        if self.current_view.view_type != 'tree':
            return self.current_model.is_modified()
        else:
            for model in self.models.models:
                if model.is_modified():
                    return True
        return False

    def reload(self):
        self.current_model.reload()
        if self.parent:
            self.parent.reload()
        self.display()

    def remove(self, unlink = False):
        id = False
        if self.current_view.view_type == 'form' and self.current_model:
            id = self.current_model.id
            
            idx = self.models.models.index(self.current_model)
            if not id:
                lst=[]
                self.models.models.remove(self.models.models[idx])
                self.current_model=None
                if self.models.models:
                    idx = min(idx, len(self.models.models)-1)
                    self.current_model = self.models.models[idx]
                self.display()
                self.current_view.set_cursor()
                return False

            ctx = self.current_model.context_get().copy()
            self.current_model.update_context_with_concurrency_check_data(ctx)
            if unlink and id:
                if not self.rpc.unlink([id], ctx):
                    return False

            self.models.remove(self.current_model)
            if self.models.models:
                idx = min(idx, len(self.models.models)-1)
                self.current_model = self.models.models[idx]
            else:
                self.current_model = None
            self.display()
            self.current_view.set_cursor()
        if self.current_view.view_type == 'tree':
            ids = self.current_view.sel_ids_get()
            
            ctx = self.models.context.copy()
            for m in self.models:
                if m.id in ids:
                    m.update_context_with_concurrency_check_data(ctx)

            if unlink and ids:
                if not self.rpc.unlink(ids, ctx):
                    return False
            for model in self.current_view.sel_models_get():
                self.models.remove(model)
            self.current_model = None
            self.display()
            self.current_view.set_cursor()
            id = ids
        return id

    def load(self, ids):
        limit = self.screen_container.get_limit()
        if limit:
            tot_rec = rpc.session.rpc_exec_auth_try('/object', 'execute', self.name, 'search_count', [], self.context)
            if limit < tot_rec:
                self.screen_container.fill_limit_combo(tot_rec)        
        self.models.load(ids, display=False)
        self.current_view.reset()
        if ids:
            self.display(ids[0])
        else:
            self.current_model = None
            self.display()

    def display(self, res_id=None):
        if res_id:
            self.current_model = self.models[res_id]
        if self.views:
            self.current_view.display()
            self.current_view.widget.set_sensitive(bool(self.models.models or (self.current_view.view_type!='form') or self.current_model))
            vt = self.current_view.view_type
            self.search_active(
                    active=self.show_search and vt in ('tree', 'graph', 'calendar'),
                    show_search=self.show_search and vt in ('tree', 'graph','calendar'),
            )

    def display_next(self):
        self.current_view.set_value()
        if self.current_model in self.models.models:
            idx = self.models.models.index(self.current_model)
            idx = (idx+1) % len(self.models.models)
            self.current_model = self.models.models[idx]
        else:
            self.current_model = len(self.models.models) and self.models.models[0]
        if self.current_model:
            self.current_model.validate_set()
        self.display()
        self.current_view.set_cursor()

    def display_prev(self):
        self.current_view.set_value()
        if self.current_model in self.models.models:
            idx = self.models.models.index(self.current_model)-1
            if idx<0:
                idx = len(self.models.models)-1
            self.current_model = self.models.models[idx]
        else:
            self.current_model = len(self.models.models) and self.models.models[-1]

        if self.current_model:
            self.current_model.validate_set()
        self.display()
        self.current_view.set_cursor()

    def sel_ids_get(self):
        return self.current_view.sel_ids_get()

    def id_get(self):
        if not self.current_model:
            return False
        return self.current_model.id

    def ids_get(self):
        return [x.id for x in self.models if x.id]

    def clear(self):
        self.models.clear()

    def on_change(self, callback):
        self.current_model.on_change(callback)
        self.display()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

