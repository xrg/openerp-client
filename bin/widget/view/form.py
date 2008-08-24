# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import gtk
from gtk import glade

import common
import rpc
import service
import options
from form_gtk.action import action
from form_gtk.parser import Button
from interface import parser_view
import tools

class ViewWidget(object):
    def __init__(self, parent, widget, widget_name):
        self.view_form = parent
        self.widget = widget
        self.widget._view = self
        self.widget_name = widget_name

    def display(self, model, state='draft'):
        if not model:
            self.widget.display(model, False)
            return False
        modelfield = model.mgroup.mfields.get(self.widget_name, False)
        if modelfield:
            modelfield.state_set(model, state)
            if modelfield.attrs.get('attrs',False):
                modelfield.attrs_set(model)
            self.widget.display(model, modelfield)
        elif isinstance(self.widget, action):
            self.widget.display(model, False)

    def reset(self, model):
        modelfield = False
        if model:
            modelfield = model.mgroup.mfields.get(self.widget_name, False)
            if modelfield and 'valid' in modelfield.get_state_attrs(model):
                modelfield.get_state_attrs(model)['valid'] = True
        self.display(model, modelfield)

    def set_value(self, model):
        if self.widget_name in model.mgroup.mfields:
            self.widget.set_value(model, model.mgroup.mfields[self.widget_name])

    def _get_model(self):
        return self.view_form.screen.current_model

    model = property(_get_model)

    def _get_modelfield(self):
        if self.model:
            return self.model.mgroup.mfields[self.widget_name]

    modelfield = property(_get_modelfield)

class ViewForm(parser_view):
    def __init__(self, window, screen, widget, children=None,
            state_aware_widgets=None, toolbar=None):
        super(ViewForm, self).__init__(window, screen, widget, children,
                state_aware_widgets, toolbar)
        self.view_type = 'form'
        self.model_add_new = False

        for w in self.state_aware_widgets:
            if isinstance(w.widget, Button):
                w.widget.form = self

        self.widgets = dict([(name, ViewWidget(self, widget, name))
                             for name, widget in children.items()])

        if toolbar and not options.options['client.modepda']:
            hb = gtk.HBox()
            hb.pack_start(self.widget)

            #tb = gtk.Toolbar()
            #tb.set_orientation(gtk.ORIENTATION_VERTICAL)
            #tb.set_style(gtk.TOOLBAR_BOTH_HORIZ)
            #tb.set_icon_size(gtk.ICON_SIZE_MENU)
            tb = gtk.VBox()

            eb = gtk.EventBox()
            eb.add(tb)
            eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("lightgrey"))
            #tb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("blue"))


            hb.pack_start(eb, False, False)
            self.widget = hb



            sep = False
            for icontype in ('print', 'action', 'relate'):
                if icontype in ('action','relate') and sep:
                    #tb.insert(gtk.SeparatorToolItem(), -1)
                    tb.pack_start(gtk.HSeparator(), False, False, 2)
                    sep = False
                for tool in toolbar[icontype]:
                    iconstock = {
                        'print': gtk.STOCK_PRINT,
                        'action': gtk.STOCK_EXECUTE,
                        'relate': gtk.STOCK_JUMP_TO,
                    }.get(icontype, gtk.STOCK_ABOUT)



                    icon = gtk.Image()
                    icon.set_from_stock(iconstock, gtk.ICON_SIZE_BUTTON)
                    hb = gtk.HBox(False, 5)
                    hb.pack_start(icon, False, False)
                    hb.pack_start(gtk.Label(tool['string']), False, False)

                    tbutton = gtk.Button()
                    tbutton.add(hb)
                    tbutton.set_relief(gtk.RELIEF_NONE)
                    tb.pack_start(tbutton, False, False, 2)

                    #tbutton = gtk.ToolButton()
                    #tbutton.set_label_widget(hb) #tool['string'])
                    #tbutton.set_stock_id(iconstock)
                    #tb.insert(tbutton,-1)

                    def _action(button, action, type):
                        data={}
                        context=self.screen.context
                        act=action.copy()
                        if type in ('print', 'action'):
                            self.screen.save_current()
                            id = self.screen.current_model and self.screen.current_model.id
                            if not (id):
                                common.message(_('You must save this record to use the relate button !'))
                                return False
                            self.screen.display()
                            data = {
                                'model': self.screen.name,
                                'id': id,
                                'ids': [id],
                                'report_type': act.get('report_type', 'pdf'),
                            }
                        if type == 'relate':
                            id = self.screen.current_model and self.screen.current_model.id
                            if not (id):
                                common.message(_('You must select a record to use the relate button !'))
                                return False
                            act['domain'] = self.screen.current_model.expr_eval(act['domain'], check_load=False)
                            act['context'] = str(self.screen.current_model.expr_eval(act['context'], check_load=False))
                        obj = service.LocalService('action.main')
                        value = obj._exec_action(act, data, context)
                        if type in ('print', 'action'):
                            self.screen.reload()
                        return value

                    def _translate_label(self, event, tool, window):
                        if event.button != 3:
                            return False
                        def callback(self, tool, window):
                            lang_ids = rpc.session.rpc_exec_auth('/object',
                                    'execute', 'res.lang', 'search',
                                    [('translatable', '=', '1')])
                            if not lang_ids:
                                common.message(_('No other language available!'),
                                        parent=window)
                                return False
                            langs = rpc.session.rpc_exec_auth('/object',
                                    'execute', 'res.lang', 'read', lang_ids,
                                    ['code', 'name'])

                            win = gtk.Dialog(_('Add Translation'), window,
                                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
                            win.vbox.set_spacing(5)
                            win.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
                            win.set_icon(common.TINYERP_ICON)
                            vbox = gtk.VBox(spacing=5)

                            entries_list = []
                            for lang in langs:
                                code = lang['code']
                                val = rpc.session.rpc_exec_auth('/object',
                                        'execute', tool['type'], 'read',
                                        [tool['id']], ['name'], {'lang': code})
                                val = val[0]

                                label = gtk.Label(lang['name'])
                                entry = gtk.Entry()
                                entry.set_text(val['name'])
                                entries_list.append((code, entry))
                                hbox = gtk.HBox(homogeneous=True)
                                hbox.pack_start(label, expand=False, fill=False)
                                hbox.pack_start(entry, expand=True, fill=True)
                                vbox.pack_start(hbox, expand=False, fill=True)

                            vp = gtk.Viewport()
                            vp.set_shadow_type(gtk.SHADOW_NONE)
                            vp.add(vbox)
                            sv = gtk.ScrolledWindow()
                            sv.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
                            sv.set_shadow_type(gtk.SHADOW_NONE)
                            sv.add(vp)
                            win.vbox.add(sv)
                            win.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
                            win.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
                            win.resize(400,200)
                            win.show_all()
                            res = win.run()
                            if res == gtk.RESPONSE_OK:
                                to_save = map(lambda x: (x[0],
                                    x[1].get_text()), entries_list)
                                while to_save:
                                    code, val = to_save.pop()
                                    rpc.session.rpc_exec_auth('/object',
                                            'execute', tool['type'],
                                            'write', [tool['id']],
                                            {'name': val}, {'lang': code})
                            window.present()
                            win.destroy()
                            return res

                        menu = gtk.Menu()
                        item = gtk.ImageMenuItem(_('Translate label'))
                        item.connect("activate", callback, tool, window)
                        item.set_sensitive(1)
                        item.show()
                        menu.append(item)
                        menu.popup(None,None,None,event.button,event.time)
                        return True

                    tbutton.connect('clicked', _action, tool, icontype)

                    tbutton.connect('button_press_event', _translate_label,
                            tool, self.window)

                    sep = True


    def __getitem__(self, name):
        return self.widgets[name]

    def destroy(self):
        self.widget.destroy()
        for widget in self.widgets.keys():
            self.widgets[widget].widget.destroy()
            del self.widgets[widget]
        del self.widget
        del self.widgets
        del self.screen
        del self.state_aware_widgets

    def cancel(self):
        pass

    def set_value(self):
        model = self.screen.current_model
        if model:
            for widget in self.widgets.values():
                widget.set_value(model)

    def sel_ids_get(self):
        if self.screen.current_model:
            return [self.screen.current_model.id]
        return []

    def sel_models_get(self):
        if self.screen.current_model:
            return [self.screen.current_model]
        return []

    def reset(self):
        model = self.screen.current_model
        for wid_name, widget in self.widgets.items():
            widget.reset(model)

    def signal_record_changed(self, *args):
        pass

    def attrs_set(self, model, obj, att_obj):
        attrs_changes = eval(att_obj.attrs.get('attrs',"{}"))
        for k,v in attrs_changes.items():
			for condition in v:
				result = tools.calc_condition(self,model,condition)
				if result:
					if k=='invisible':
						obj.hide()
					elif k=='readonly':
						obj.set_sensitive(False)
				else:
					if k=='invisible':
						obj.show()
					if k=='readonly':
						obj.set_sensitive(True)

    def set_notebook(self,model,nb):
        for i in range(0,nb.get_n_pages()):
            if nb.get_tab_label(nb.get_nth_page(i)).attrs.get('attrs',False):
                self.attrs_set(model,nb.get_nth_page(i),nb.get_tab_label(nb.get_nth_page(i)))

    def display(self):
        model = self.screen.current_model
        for x in self.widget.get_children():
            if (type(x)==gtk.Table):
                for y in x.get_children():
                    if type(y)==gtk.Notebook:
                        self.set_notebook(model,y)
            elif type(x)==gtk.Notebook:
                self.set_notebook(model,x)
        if model and ('state' in model.mgroup.fields):
            state = model['state'].get(model)
        else:
            state = 'draft'
        for widget in self.widgets.values():
            widget.display(model, state)
        for widget in self.state_aware_widgets:
            widget.state_set(state)
            widget.attrs_set(model)
        return True

    def set_cursor(self, new=False):
        pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

