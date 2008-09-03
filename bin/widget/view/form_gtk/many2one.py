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

import gobject
import gtk
import copy

import gettext

import interface
import wid_common
import common

import widget
from widget.screen import Screen

from modules.gui.window.win_search import win_search
import rpc

import service


class dialog(object):
    def __init__(self, model, id=None, attrs=None ,domain=None, context=None, window=None, view_ids=None,target=False):
        if attrs is None:
            attrs = {}
        if domain is None:
            domain = []
        if context is None:
            context = {}

        if not window:
            window = service.LocalService('gui.main').window

        self.dia = gtk.Dialog(_('OpenERP - Link'), window,
                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT)
        self.window = window
        if ('string' in attrs) and attrs['string']:
            self.dia.set_title(self.dia.get_title() + ' - ' + attrs['string'])
        if not target:
            self.dia.set_property('default-width', 760)
            self.dia.set_property('default-height', 500)
            self.dia.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
            self.dia.set_icon(common.TINYERP_ICON)

            self.accel_group = gtk.AccelGroup()
            self.dia.add_accel_group(self.accel_group)

            self.but_cancel = self.dia.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            self.but_cancel.add_accelerator('clicked', self.accel_group, gtk.keysyms.Escape, gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

            self.but_ok = self.dia.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
            self.but_ok.add_accelerator('clicked', self.accel_group, gtk.keysyms.Return, gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_placement(gtk.CORNER_TOP_LEFT)
        scroll.set_shadow_type(gtk.SHADOW_NONE)
        self.dia.vbox.pack_start(scroll, expand=True, fill=True)

        vp = gtk.Viewport()
        vp.set_shadow_type(gtk.SHADOW_NONE)
        scroll.add(vp)
        self.screen = Screen(model, view_ids=view_ids, domain=domain, context=context, window=self.dia, view_type=['form'])
        if id:
            self.screen.load([id])
        else:
            self.screen.new()
        vp.add(self.screen.widget)

        x,y = self.screen.screen_container.size_get()
        width, height = window.get_size()
        vp.set_size_request(min(width - 20, x + 20),min(height - 60, y + 25))
        self.dia.show_all()
        self.screen.display()

    def run(self, datas={}):
        while True:
            res = self.dia.run()
            if res==gtk.RESPONSE_OK:
                if self.screen.current_model.validate() and self.screen.save_current():
                    return (True, self.screen.current_model.name_get())
                else:
                    self.screen.display()
            else:
                break
        return (False, False)

    def destroy(self):
        self.window.present()
        self.dia.destroy()

class many2one(interface.widget_interface):
    def __init__(self, window, parent, model, attrs={}):
        interface.widget_interface.__init__(self, window, parent, model, attrs)

        self.widget = gtk.HBox(spacing=3)
        self.widget.set_property('sensitive', True)
        self.widget.connect('focus-in-event', lambda x,y: self._focus_in())
        self.widget.connect('focus-out-event', lambda x,y: self._focus_out())

        self.wid_text = gtk.Entry()
        self.wid_text.set_property('width-chars', 13)
        self.wid_text.connect('key_press_event', self.sig_key_press)
        self.wid_text.connect('button_press_event', self._menu_open)
        self.wid_text.connect_after('changed', self.sig_changed)
        self.wid_text.connect_after('activate', self.sig_activate)
        self.wid_text_focus_out_id = self.wid_text.connect_after('focus-out-event', self.sig_focus_out, True)
        self.widget.pack_start(self.wid_text, expand=True, fill=True)

        self.but_find = gtk.Button()
        img_find = gtk.Image()
        img_find.set_from_stock('gtk-find',gtk.ICON_SIZE_BUTTON)
        self.but_find.set_image(img_find)
        self.but_find.set_relief(gtk.RELIEF_NONE)
        self.but_find.connect('clicked', self.sig_find)
        self.but_find.set_alignment(0.5, 0.5)
        self.but_find.set_property('can-focus', False)

        self.tooltips = gtk.Tooltips()
        self.tooltips.set_tip(self.but_find, _('Select a record'))
        self.tooltips.enable()


        self.but_open = gtk.Button()
        img_open = gtk.Image()
        img_open.set_from_stock('gtk-open',gtk.ICON_SIZE_BUTTON)
        self.but_open.set_image(img_open)
        self.but_open.set_relief(gtk.RELIEF_NONE)
        self.but_open.connect('clicked', self.sig_edit)
        self.but_open.set_alignment(0.5, 0.5)
        self.but_open.set_property('can-focus', False)

        self.tooltips = gtk.Tooltips()
        self.tooltips.set_tip(self.but_find, _('Open this record'))
        self.tooltips.enable()

        self.widget.pack_start(self.but_open, padding=2, expand=False, fill=False)
        self.widget.pack_start(self.but_find, padding=2, expand=False, fill=False)

        self.ok = True
        self._readonly = False
        self.model_type = attrs['relation']
        self._menu_loaded = False
        self._menu_entries.append((None, None, None))
        self._menu_entries.append((_('Action'), lambda x: self.click_and_action('client_action_multi'),0))
        self._menu_entries.append((_('Report'), lambda x: self.click_and_action('client_print_multi'),0))

        if attrs.get('completion',False):
            ids = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['relation'], 'name_search', '', [], 'ilike', {})
            if ids:
                self.load_completion(ids,attrs)

    def load_completion(self,ids,attrs):
        self.completion = gtk.EntryCompletion()
        self.completion.set_match_func(self.match_func, None)
        self.completion.connect("match-selected", self.on_completion_match)
        self.wid_text.set_completion(self.completion)
        self.liststore = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.completion.set_model(self.liststore)
        self.completion.set_text_column(0)
        for i,word in enumerate(ids):
            if word[1][0] == '[':
                i = word[1].find(']')
                s = word[1][1:i]
                s2 = word[1][i+2:]
                self.liststore.append([("%s %s" % (s,s2)),s2])
            else:
                self.liststore.append([word[1],word[1]])

    def match_func(self, completion, key_string, iter, data):
        model = self.completion.get_model()
        modelstr = model[iter][0].lower()
        return modelstr.startswith(key_string)

    def on_completion_match(self, completion, model, iter):
        name = model[iter][1]
        domain = self._view.modelfield.domain_get(self._view.model)
        context = self._view.modelfield.context_get(self._view.model)
        ids = rpc.session.rpc_exec_auth('/object', 'execute',
                self.attrs['relation'], 'name_search', name, domain, 'ilike',
                context)
        if len(ids)==1:
            self._view.modelfield.set_client(self._view.model, ids[0])
            self.display(self._view.model, self._view.modelfield)
            self.ok = True
        else:
            win = win_search(self.attrs['relation'], sel_multi=False,
                    ids=map(lambda x: x[0], ids), context=context,
                    domain=domain, window=self._window)
            ids = win.go()
            if ids:
                name = rpc.session.rpc_exec_auth('/object', 'execute',
                        self.attrs['relation'], 'name_get', [ids[0]],
                        rpc.session.context)[0]
                self._view.modelfield.set_client(self._view.model, name)
        return True

    def _readonly_set(self, value):
        self._readonly = value
        self.wid_text.set_editable(not value)
        #self.but_new.set_sensitive(not value)

    def _color_widget(self):
        return self.wid_text

    def _menu_sig_pref(self, obj):
        self._menu_sig_default_set()

    def _menu_sig_default(self, obj):
        res = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['model'], 'default_get', [self.attrs['name']])

    def sig_find(self, widget, event=None, leave=False):
        self.ok = False
        self.wid_text.disconnect(self.wid_text_focus_out_id)
        if not self._readonly:
            domain = self._view.modelfield.domain_get(self._view.model)
            context = self._view.modelfield.context_get(self._view.model)
            self.wid_text.grab_focus()

            ids = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['relation'], 'name_search', leave and self.wid_text.get_text() or '', domain, 'ilike', context)
            if (len(ids)==1) and leave:
                self._view.modelfield.set_client(self._view.model, ids[0],
                        force_change=True)
                self.wid_text_focus_out_id = self.wid_text.connect_after('focus-out-event', self.sig_focus_out, True)
                self.display(self._view.model, self._view.modelfield)
                self.ok = True
                return True

            win = win_search(self.attrs['relation'], sel_multi=False, ids=map(lambda x: x[0], ids), context=context, domain=domain, parent=self._window)
            ids = win.go()
            if ids:
                name = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['relation'], 'name_get', [ids[0]], rpc.session.context)[0]
                self._view.modelfield.set_client(self._view.model, name,
                        force_change=True)
        self.wid_text_focus_out_id = self.wid_text.connect_after('focus-out-event', self.sig_focus_out, True)
        self.display(self._view.model, self._view.modelfield)
        self.ok=True

    def sig_edit(self, widget, event=None, leave=False):
        self.ok = False
        self.wid_text.disconnect(self.wid_text_focus_out_id)
        if not leave:
            domain = self._view.modelfield.domain_get(self._view.model)
            context = self._view.modelfield.context_get(self._view.model)
            dia = dialog(self.attrs['relation'], self._view.modelfield.get(self._view.model), attrs=self.attrs, window=self._window, domain=domain, context=context)
            ok, value = dia.run()
            if ok:
                self._view.modelfield.set_client(self._view.model, value,
                        force_change=True)
            dia.destroy()
        self.wid_text_focus_out_id = self.wid_text.connect_after('focus-out-event', self.sig_focus_out, True)
        self.display(self._view.model, self._view.modelfield)
        self.ok=True

    def sig_focus_out(self, widget, event=None, leave=False):
        res = self._view.modelfield.get_client(self._view.model)
        if self.wid_text.get_text() and not res:
            self.sig_find(widget, event, leave=True)

    def sig_activate(self, widget, event=None, leave=False):
        self.sig_find(widget, event, leave=True)

    def sig_new(self, *args):
        self.wid_text.disconnect(self.wid_text_focus_out_id)
        domain = self._view.modelfield.domain_get(self._view.model)
        context = self._view.modelfield.context_get(self._view.model)
        dia = dialog(self.attrs['relation'], attrs=self.attrs, window=self._window, domain=domain ,context=context)
        ok, value = dia.run()
        if ok:
            self._view.modelfield.set_client(self._view.model, value)
            self.display(self._view.model, self._view.modelfield)
        dia.destroy()
        self.wid_text_focus_out_id = self.wid_text.connect_after('focus-out-event', self.sig_focus_out, True)

    def sig_key_press(self, widget, event, *args):
        if event.keyval==gtk.keysyms.F1:
            self.sig_new(widget, event)
        elif event.keyval==gtk.keysyms.F2:
            self.sig_activate(widget, event)
        elif event.keyval  == gtk.keysyms.Tab:
            if self._view.modelfield.get(self._view.model) or \
                    not self.wid_text.get_text():
                return False
            self.sig_activate(widget, event, leave=True)
            return True
        return False

    def sig_changed(self, *args):
        if self.ok:
            if self._view.modelfield.get(self._view.model):
                self._view.modelfield.set_client(self._view.model, False)
                self.display(self._view.model, self._view.modelfield)
        return False

    def set_value(self, model, model_field):
        pass # No update of the model, the model is updated in real time !

    def display(self, model, model_field):
        if not model_field:
            self.ok = False
            self.wid_text.set_text('')
            return False
        super(many2one, self).display(model, model_field)
        self.ok=False
        res = model_field.get_client(model)
        self.wid_text.set_text((res and str(res)) or '')
        self.but_open.set_sensitive(bool(res))
        self.ok=True

    def _menu_open(self, obj, event):
        if event.button == 3:
            value = self._view.modelfield.get(self._view.model)
            if not self._menu_loaded:
                resrelate = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.values', 'get', 'action', 'client_action_relate', [(self.model_type, False)], False, rpc.session.context)
                resrelate = map(lambda x:x[2], resrelate)
                self._menu_entries.append((None, None, None))
                for x in resrelate:
                    x['string'] = x['name']
                    f = lambda action: lambda x: self.click_and_relate(action)
                    self._menu_entries.append(('... '+x['name'], f(x), 0))
            self._menu_loaded = True

            menu = gtk.Menu()
            for stock_id,callback,sensitivity in self._menu_entries:
                if stock_id:
                    item = gtk.ImageMenuItem(stock_id)
                    if callback:
                        item.connect("activate",callback)
                    item.set_sensitive(bool(sensitivity or value))
                else:
                    item=gtk.SeparatorMenuItem()
                item.show()
                menu.append(item)
            menu.popup(None,None,None,event.button,event.time)
            return True
        return False

    def click_and_relate(self, action):
        data={}
        context={}
        act=action.copy()
        id = self._view.modelfield.get(self._view.model)
        if not(id):
            common.message(_('You must select a record to use the relation !'))
            return False
        screen = Screen(self.attrs['relation'])
        screen.load([id])
        act['domain'] = screen.current_model.expr_eval(act['domain'], check_load=False)
        act['context'] = str(screen.current_model.expr_eval(act['context'], check_load=False))
        obj = service.LocalService('action.main')
        value = obj._exec_action(act, data, context)
        return value

    def click_and_action(self, type):
        id = self._view.modelfield.get(self._view.model)
        obj = service.LocalService('action.main')
        res = obj.exec_keyword(type, {'model':self.model_type, 'id': id or False, 'ids':[id], 'report_type': 'pdf'})
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

