# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyright (c) 2008-2009 B2CK, Bertrand Chenal, Cedric Krier (D&D in lists)
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

import gobject
import gtk
import tools

import rpc
import service
import locale
from interface import parser_view


class AdaptModelGroup(gtk.GenericTreeModel):

    def __init__(self, model_group):
        super(AdaptModelGroup, self).__init__()
        self.model_group = model_group
        self.models = model_group.models
        self.last_sort = None
        self.sort_asc = True
        self.groupBY = False
        self.o2M_group = self.model_group.one2many
        self.parent_child = {}
        self.parent_keys = []
        self.old = []
        self.set_property('leak_references', False)
        if self.o2M_group:
            self.set_o2m_Models(self.models)


    def set_o2m_Models(self,models):
        for model in models:
            if not model.group_by_parent:
                self.parent_keys.insert(len(self.parent_child.keys()),model)
                self.parent_child[model] = []
            else:
                self.parent_child[model.group_by_parent].append(model)

    def added(self, modellist, position):
        self.groupBY = self.model_group.groupBY
        if modellist is self.models:
            model = self.models[position]
            if self.groupBY:
                self.set_o2m_Models([model])
                self.old.append(model)
            self.emit('row_inserted', self.on_get_path(model),
                      self.get_iter(self.on_get_path(model)))

    def cancel(self):
        pass

    def changed_all(self, *args):
        self.emit('row_deleted', position)
        self.invalidate_iters()

    def move(self, path, position):
        idx = path[0]
        self.model_group.model_move(self.models[idx], position)

    def removed(self, lst, position):
        self.emit('row_deleted', position)
        self.invalidate_iters()

    def append(self, model):
        self.model_group.model_add(model)

    def prepend(self, model):
        self.model_group.model_add(model, 0)

    def remove(self, iter):
        idx = self.get_path(iter)[0]
        self.model_group.model_remove(self.models[idx])
        self.invalidate_iters()

    def sort(self, name):
        self.sort_asc = not (self.sort_asc and (self.last_sort == name))
        self.last_sort = name
        if self.sort_asc:
            f = lambda x,y: cmp(x[name].get_client(x), y[name].get_client(y))
        else:
            f = lambda x,y: -1 * cmp(x[name].get_client(x), y[name].get_client(y))
        self.models.sort(f)
        for idx, row in enumerate(self.models):
            iter = self.get_iter(idx)
            self.row_changed(self.get_path(iter), iter)

    def saved(self, id):
        return self.model_group.writen(id)

    def __len__(self):
        if self.groupBY or self.o2M_group:
            length = 0
            for val in self.parent_child.values():
                length += len(val)
            return length
        else:
            return len(self.models)

    ## Mandatory GenericTreeModel methods

    def on_get_flags(self):
        if self.groupBY or self.o2M_group:
             return gtk.TREE_MODEL_ITERS_PERSIST
        else:
            return gtk.TREE_MODEL_LIST_ONLY

    def on_get_n_columns(self):
        return 1

    def on_get_column_type(self, index):
        return gobject.TYPE_PYOBJECT

    def on_get_path(self, iter):
        if self.groupBY or self.o2M_group:
             if iter.group_by_parent:
                 return (self.parent_keys.index(iter.group_by_parent),self.parent_child[iter.group_by_parent].index(iter))
             else:
                 return (self.parent_keys.index(iter),)
        else:
            return self.models.index(iter)

    def on_get_iter(self, path):
        if self.groupBY or self.o2M_group:
            if len(self.parent_child.keys()):
                if isinstance(path, tuple) and len(path) == 1:
                    path = path[0]
                    if path < len(self.parent_keys):
                        return self.parent_keys[path]
                    else:
                        return None
                elif isinstance(path, int):
                    path = path
                    if path < len(self.parent_keys):
                        return self.parent_keys[path]
                    else:
                        return None
                elif isinstance(path, tuple) and len(path) > 1:
                    return self.parent_child[self.parent_keys[path[0]]][path[1]]
                else:
                    return None
            else:
                return None
        else:
            if isinstance(path, tuple):
                path = path[0]
            if self.models:
                if path<len(self.models):
                    return self.models[path]
                else:
                    return None
            else:
                return None

    def on_get_value(self, node, column):
        assert column == 0
        if self.groupBY or self.o2M_group:
            if node.group_by_parent:
                return node
        return node

    def on_iter_next(self, node):
        if self.groupBY or self.o2M_group:
            try:
                if node:
                    if node.group_by_parent:
                        index = self.parent_child[node.group_by_parent].index(node)
                        return self.parent_child[node.group_by_parent][index + 1]
                    else:
                        index = self.parent_keys.index(node)
                        if index + 1 < len(self.parent_keys):
                            return self.parent_keys[index + 1]
                        return None
                else:
                    return None
            except IndexError:
                return None
        else:
            try:
                return self.on_get_iter(self.on_get_path(node) + 1)
            except IndexError:
                return None

    def on_iter_has_child(self, node):
        if self.groupBY or self.o2M_group:
             if not node.group_by_parent:
                 return self.parent_child[node] != []
             else:
                 return False
        else:
            return False

    def on_iter_children(self, node):
        if self.groupBY or self.o2M_group:
            if node and self.parent_child:
                return self.parent_child[node][0]
            return None
        else:
            return None

    def on_iter_n_children(self, node):
        if self.groupBY or self.o2M_group:
            return len(self.parent_child[node])
        else:
            return 0

    def on_iter_nth_child(self, node, n):
        if self.groupBY or self.o2M_group:
            if node:
                 if node.group_by_parent:
                     return self.parent_child[node.group_by_parent][n]
                 else:
                     return self.parent_child[node][0]
            else:
                if self.parent_keys:
                    return self.parent_keys[n]
                return None
        else:
            if node is None and self.models:
                return self.on_get_iter(0)
            return None

    def on_iter_parent(self, node):
        if self.groupBY or self.o2M_group:
              if node.group_by_parent:
                  return node.group_by_parent
              else:
                  return None
        else:
            return None

class ViewList(parser_view):

    def __init__(self, window, screen, widget, children=None, buttons=None,
            toolbar=None, submenu=None):
        super(ViewList, self).__init__(window, screen, widget, children,
                buttons, toolbar, submenu=submenu)
        self.store = None
        self.view_type = 'tree'
        self.model_add_new = True
        self.widget = gtk.VBox()
        self.widget_tree = widget
        scroll = gtk.ScrolledWindow()
        scroll.add(self.widget_tree)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.widget.pack_start(scroll, expand=True, fill=True)
        self.widget_tree.screen = screen
        self.reload = False
        self.children = children
        self.groupBY = False
        self.o2m_group = False

        if children:
            hbox = gtk.HBox()
            self.widget.pack_start(hbox, expand=False, fill=False, padding=2)
            for c in children:
                hbox2 = gtk.HBox()
                hbox2.pack_start(children[c][1], expand=True, fill=False)
                hbox2.pack_start(children[c][2], expand=True, fill=False)
                hbox.pack_start(hbox2, expand=False, fill=False, padding=12)
            hbox.show_all()

        self.display()

        self.widget_tree.connect('button-press-event', self.__hello)
        self.widget_tree.connect_after('row-activated', self.__sig_switch)
        selection = self.widget_tree.get_selection()
        selection.set_mode(gtk.SELECTION_MULTIPLE)
        selection.connect('changed', self.__select_changed)

        if self.widget_tree.sequence:
            self.widget_tree.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
                    [('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),],
                    gtk.gdk.ACTION_MOVE)
            self.widget_tree.drag_source_set(gtk.gdk.BUTTON1_MASK | gtk.gdk.BUTTON3_MASK,
                    [('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),],
                    gtk.gdk.ACTION_MOVE)
            self.widget_tree.enable_model_drag_dest(
                    [('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),],
                    gtk.gdk.ACTION_MOVE)

            self.widget_tree.connect('drag-drop', self.drag_drop)
            self.widget_tree.connect("drag-data-get", self.drag_data_get)
            self.widget_tree.connect('drag-data-received', self.drag_data_received)
            self.widget_tree.connect('drag-data-delete', self.drag_data_delete)

    def drag_drop(self, treeview, context, x, y, time):
        treeview.emit_stop_by_name('drag-drop')
        treeview.drag_get_data(context, context.targets[-1], time)
        return True

    def drag_data_get(self, treeview, context, selection, target_id,
            etime):
        treeview.emit_stop_by_name('drag-data-get')
        def _func_sel_get(store, path, iter, data):
            data.append(path)
        data = []
        treeselection = treeview.get_selection()
        treeselection.selected_foreach(_func_sel_get, data)
        data = str(data[0])
        selection.set(selection.target, 8, data)

    def drag_data_received(self, treeview, context, x, y, selection,
            info, etime):
        treeview.emit_stop_by_name('drag-data-received')
        if treeview.sequence:
            for model in self.screen.models.models:
                if model['sequence'].get_state_attrs(
                        model).get('readonly', False):
                    return
        model = treeview.get_model()
        data = eval(selection.data)
        drop_info = treeview.get_dest_row_at_pos(x, y)
        if drop_info:
            path, position = drop_info
            idx = path[0]
            if position in (gtk.TREE_VIEW_DROP_BEFORE,
                    gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
                model.move(data, idx)
            else:
                model.move(data, idx + 1)
        context.drop_finish(False, etime)
        if treeview.sequence:
            self.screen.models.set_sequence(field='sequence')

    def drag_data_delete(self, treeview, context):
        treeview.emit_stop_by_name('drag-data-delete')

    def attrs_set(self, model,path):
        if path.attrs.get('attrs',False):
            attrs_changes = eval(path.attrs.get('attrs',"{}"),{'uid':rpc.session.uid})
            for k,v in attrs_changes.items():
                result = True
                for condition in v:
                    result = tools.calc_condition(self,model,condition)
                if result:
                    if k=='invisible':
                        return False
                    elif k=='readonly':
                        return False
        return True

    def __hello(self, treeview, event, *args):

        if event.button in [1,3]:
            path = treeview.get_path_at_pos(int(event.x),int(event.y))
            selection = treeview.get_selection()
            if selection.get_mode() == gtk.SELECTION_SINGLE:
                model, iter = selection.get_selected()
            elif selection.get_mode() == gtk.SELECTION_MULTIPLE:
                model, paths = selection.get_selected_rows()
            if (not path) or not path[0]:
                return False
            m = model.models[path[0][0]]
            # TODO: add menu cache
            if event.button == 1:
                # first click on button
                if path[1]._type == 'Button':
                    cell_button = path[1].get_cells()[0]
                    # Calling actions

                    attrs_check = self.attrs_set(m,path[1])
                    if attrs_check and m['state'].get(m) in path[1].attrs['states'].split(','):
                        m.get_button_action(self.screen,m.id,path[1].attrs)
                        self.screen.current_model = m
                        self.screen.reload()
                        treeview.screen.reload()

            else:
                # Here it goes for right click
                if path[1]._type=='many2one':
                    value = m[path[1].name].get(m)
                    resrelate = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.values', 'get', 'action', 'client_action_relate', [(self.screen.fields[path[1].name]['relation'], False)], False, rpc.session.context)
                    resrelate = map(lambda x:x[2], resrelate)
                    menu = gtk.Menu()
                    for x in resrelate:
                        x['string'] = x['name']
                        item = gtk.ImageMenuItem('... '+x['name'])
                        f = lambda action, value, model: lambda x: self._click_and_relate(action, value, model)
                        item.connect('activate', f(x, value, self.screen.fields[path[1].name]['relation']))
                        item.set_sensitive(bool(value))
                        item.show()
                        menu.append(item)
                    menu.popup(None,None,None,event.button,event.time)

    def _click_and_relate(self, action, value, model):
        data={}
        context={}
        act=action.copy()
        if not(value):
            common.message(_('You must select a record to use the relation !'))
            return False
        from widget.screen import Screen
        screen = Screen(model)
        screen.load([value])
        act['domain'] = screen.current_model.expr_eval(act['domain'], check_load=False)
        act['context'] = str(screen.current_model.expr_eval(act['context'], check_load=False))
        obj = service.LocalService('action.main')
        value = obj._exec_action(act, data, context)
        return value


    def signal_record_changed(self, signal, *args):
        if not self.store:
            return
        if signal=='record-added':
            if self.screen.models.models<>self.widget_tree.get_model().old and self.groupBY:
                self.store = AdaptModelGroup(self.screen.models)
            self.store.added(*args)
            if self.groupBY:
                self.widget_tree.set_model(self.store)
                self.groupBY = False
        elif signal=='record-removed':
            self.store.removed(*args)
        else:
            pass
        self.update_children()

    def cancel(self):
        pass

    def __str__(self):
        return 'ViewList (%s)' % self.screen.resource

    def __getitem__(self, name):
        return None

    def destroy(self):
        self.widget_tree.destroy()
        del self.screen
        del self.widget_tree
        del self.widget

    def __sig_switch(self, treeview, *args):
        if self.groupBY or self.o2m_group:
            if len(args[0])<= 1:
                return
        self.screen.row_activate(self.screen)

    def __select_changed(self, tree_sel):
        if tree_sel.get_mode() == gtk.SELECTION_SINGLE:
            model, iter = tree_sel.get_selected()
            if iter:
                path = model.get_path(iter)[0]
                self.screen.current_model = model.models[path]
        elif tree_sel.get_mode() == gtk.SELECTION_MULTIPLE:
            model, paths = tree_sel.get_selected_rows()
            if paths:
                if self.groupBY or self.o2m_group:
                    if len(paths[0]) > 1:
                        self.screen.current_model = self.store.parent_child[self.store.parent_keys[paths[0][0]]][paths[0][1]]
                    else:
                        self.screen.current_model = self.store.parent_keys[paths[0][0]]
                else:
                    self.screen.current_model = model.models[paths[0][0]]
        self.update_children()


    def set_value(self):
        if self.widget_tree.editable:
            self.widget_tree.set_value()

    def reset(self):
        pass
    #
    # self.widget.set_model(self.store) could be removed if the store
    # has not changed -> better ergonomy. To test
    #
    def display(self):
        self.groupBY = self.screen.models.groupBY
        self.o2m_group = self.screen.models.one2many
        if self.o2m_group:
            self.groupBY = True
        if self.groupBY and not self.o2m_group:
            return
        if self.reload or (not self.widget_tree.get_model()) or self.screen.models<>self.widget_tree.get_model().model_group or not self.groupBY:
            self.store = AdaptModelGroup(self.screen.models)
            if self.store:
                self.widget_tree.set_model(self.store)
            self.o2m_group =  False
        self.reload = False
        if not self.screen.current_model:
            #
            # Should find a simpler solution to do something like
            #self.widget.set_cursor(None,None,False)
            #
            if self.store:
                self.widget_tree.set_model(self.store)
        self.update_children()

    def update_children(self):
        ids = self.sel_ids_get()
        for c in self.children:
            value = 0.0
            for model in self.screen.models.models:
                if model.id in ids or not ids:
                    value += model.fields_get()[self.children[c][0]].get(model, check_load=False)
            label_str = tools.locale_format('%.' + str(self.children[c][3]) + 'f', value)
            if self.children[c][4]:
                self.children[c][2].set_markup('<b>%s</b>' % label_str)
            else:
                self.children[c][2].set_markup(label_str)

    def set_cursor(self, new=False):
        if self.screen.current_model:
            path = self.store.on_get_path(self.screen.current_model)
            columns = self.widget_tree.get_columns(include_non_visible=False, include_non_editable=False)
            focus_column = len(columns) and columns[0] or None
            self.widget_tree.set_cursor(path, focus_column, new)

    def sel_ids_get(self):
        def _func_sel_get(store, path, iter, ids):
            model = store.on_get_iter(path)
            if self.groupBY or self.o2m_group:
                if model.id and model.group_by_parent:
                    ids.append(model.id)
            else:
                if model.id:
                    ids.append(model.id)
        ids = []
        sel = self.widget_tree.get_selection()
        if sel:
            sel.selected_foreach(_func_sel_get, ids)
        return ids

    def expand_row(self,path,open_all):
        self.widget_tree.expand_row(path,open_all)

    def collapse_row(self,path):
        self.widget_tree.collapse_row(path)

    def sel_models_get(self):
        def _func_sel_get(store, path, iter, models):
            models.append(store.on_get_iter(path))
        models = []
        sel = self.widget_tree.get_selection()
        sel.selected_foreach(_func_sel_get, models)
        return models

    def on_change(self, callback):
        self.set_value()
        self.screen.on_change(callback)

    def unset_editable(self):
        self.widget_tree.editable = False
        for col in self.widget_tree.get_columns():
            for renderer in col.get_cell_renderers():
                if isinstance(renderer, gtk.CellRendererToggle):
                    renderer.set_property('activatable', False)
                elif not isinstance(renderer, gtk.CellRendererProgress):
                    renderer.set_property('editable', False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

