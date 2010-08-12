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

import gtk
from gtk import glade
import gobject
import gettext
import common
import service

import rpc

from widget.screen import Screen
import widget_search

fields_list_type = {
    'checkbox': gobject.TYPE_BOOLEAN
}

class dialog(object):
    def __init__(self, model, domain=None, context=None, window=None, target=False):
        if domain is None:
            domain = []
        if context is None:
            context = {}

        if not window:
            window = service.LocalService('gui.main').window

        self.dia = gtk.Dialog(_('OpenERP - Link'), window,
                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT)
        self.window = window
        if not target:
            self.dia.set_property('default-width', 760)
            self.dia.set_property('default-height', 500)
            self.dia.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
            self.dia.set_icon(common.OPENERP_ICON)

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
        self.screen = Screen(model, view_ids=None, domain=domain, context=context, window=self.dia, view_type=['form'])
        self.screen.new()
        vp.add(self.screen.widget)

        x,y = self.screen.screen_container.size_get()
        width, height = window.get_size()
        vp.set_size_request(min(width - 20, x + 20),min(height - 60, y + 25))
        self.dia.show_all()
        self.screen.display()

    def run(self, datas={}):
        while True:
            try:
                res = self.dia.run()
                if res==gtk.RESPONSE_OK:
                    if self.screen.current_model.validate() and self.screen.save_current():
                        return self.screen.current_model.id
                    else:
                        self.screen.display()
                else:
                    break
            except Exception:
                # Passing all exceptions, most preferably the one of sql_constraint
                pass
        return False

    def destroy(self):
        self.window.present()
        self.dia.destroy()


class win_search(object):
    def __init__(self, model, sel_multi=True, ids=[], context={}, domain = [], parent=None):
        self.model = model
        self.first = True
        self.domain =domain
        self.context = context
        self.context.update(rpc.session.context)
        self.sel_multi = sel_multi
        self.offset = 0
        self.glade = glade.XML(common.terp_path("openerp.glade"),'win_search',gettext.textdomain())
        self.win = self.glade.get_widget('win_search')
        self.win.set_icon(common.OPENERP_ICON)
        if not parent:
            parent = service.LocalService('gui.main').window
        self.parent = parent
        self.win.set_transient_for(parent)

        self.screen = Screen(model, view_type=['tree'], context=self.context, parent=self.win)
        self.view = self.screen.current_view
        self.view.unset_editable()
        sel = self.view.widget_tree.get_selection()

        self.filter_widget = None
        self.search_count = 0

        if not sel_multi:
            sel.set_mode('single')
        else:
            sel.set_mode(gtk.SELECTION_MULTIPLE)

        self.screen.widget.set_spacing(5)
        self.parent_hbox = gtk.HBox(homogeneous=False, spacing=0)
        self.hbox = gtk.HBox(homogeneous=False, spacing=0)
        self.parent_hbox.pack_start(gtk.Label(''), expand=True, fill=True)
        self.parent_hbox.pack_start(self.hbox, expand=False, fill=False)

        self.limit_combo = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.combo = gtk.ComboBox(self.limit_combo)
        cell = gtk.CellRendererText()
        self.combo.pack_start(cell, True)
        self.combo.add_attribute(cell, 'text', 1)
        for lim in [[100,'100'],[200,'200'],[500,'500'],[False,'Unlimited']]:
            self.limit_combo.append(lim)
        self.combo.set_active(0)
        self.hbox.pack_start(self.combo, 0, 0)
        self.hbox.pack_start(gtk.VSeparator(),padding=3, expand=False, fill=False)

# Previous Button
        self.but_previous = gtk.Button()
        icon = gtk.Image()
        icon.set_from_stock('gtk-go-back', gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.but_previous.set_relief(gtk.RELIEF_NONE)
        self.but_previous.set_image(icon)
        self.hbox.pack_start(self.but_previous, 0, 0)
        self.but_previous.connect('clicked', self.search_offset_previous)

#Forward button
        icon2 = gtk.Image()
        icon2.set_from_stock('gtk-go-forward', gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.but_next = gtk.Button()
        self.but_next.set_image(icon2)
        self.but_next.set_relief(gtk.RELIEF_NONE)
        self.hbox.pack_start(self.but_next, 0, 0)
        self.but_next.connect('clicked', self.search_offset_next)

        self.screen.widget.pack_start(self.parent_hbox, expand=False, fill=False)
        self.screen.screen_container.show_filter()
        vp = gtk.Viewport()
        vp.set_shadow_type(gtk.SHADOW_NONE)
        vp.add(self.screen.widget)
        sw = self.glade.get_widget('search_sw')
        sw.add(vp)
        sw.show_all()
        self.view.widget_tree.connect('row_activated', self.sig_activate)
        self.view.widget_tree.connect('button_press_event', self.sig_button)

        self.model_name = model

        view_form = rpc.session.rpc_exec_auth('/object', 'execute', self.model_name, 'fields_view_get', False, 'search', self.context)
        hda = (self, self.find)
        self.form = widget_search.form(view_form['arch'], view_form['fields'], model, parent=self.win, col=5, call= hda)
        self.screen.filter_widget = self.form

        self.title = _('OpenERP Search: %s') % self.form.name
        self.title_results = _('OpenERP Search: %s (%%d result(s))') % (self.form.name.replace('%',''),)
        self.win.set_title(self.title)
        x, y = self.form.widget.size_request()

        hbox = self.glade.get_widget('search_hbox')
        hbox.pack_start(self.form.widget)
        self.ids = ids
        if self.ids:
            self.reload()
        self.old_search = None
        self.old_offset = self.old_limit = None
        if self.ids:
            self.old_search = []
            self.old_limit = self.get_limit()
            self.old_offset = self.offset

        self.view.widget.show_all()
        if self.form.focusable:
            self.form.focusable.grab_focus()

    def sig_activate(self, treeview, path, column, *args):
        self.view.widget_tree.emit_stop_by_name('row_activated')
        if not self.sel_multi:
            self.win.response(gtk.RESPONSE_OK)
        return False

    def sig_button(self, view, event):
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            self.win.response(gtk.RESPONSE_OK)
        return False

    def find(self, widget=None, *args):
        limit = self.get_limit()
        offset = self.offset
        if (self.old_search == self.form.value.get('domain',[])) and (self.old_limit==limit) and (self.old_offset==offset) and not self.first and widget:
            self.win.response(gtk.RESPONSE_OK)
            return False
        self.first = False
        self.old_offset = offset
        self.old_limit = limit
        v = self.form.value.get('domain',[])
        v += self.domain
        try:
            self.ids = rpc.session.rpc_exec_auth_try('/object', 'execute', self.model_name, 'search', v, offset, limit, 0, self.context)
        except:
            # Try if it is not an old server
            self.ids = rpc.session.rpc_exec_auth('/object', 'execute', self.model_name, 'search', v, offset, limit)

        self.reload()
        self.old_search = self.form.value.get('domain',[])
        self.win.set_title(self.title_results % len(self.ids))
        if len(self.ids) < limit:
            self.search_count = len(self.ids)
        else:
            self.search_count = rpc.session.rpc_exec_auth_try('/object', 'execute', self.model_name, 'search_count', [], self.context)
        if offset<=0:
            self.but_previous.set_sensitive(False)
        else:
            self.but_previous.set_sensitive(True)
        if not limit or offset+limit >= self.search_count:
            self.but_next.set_sensitive(False)
        else:
            self.but_next.set_sensitive(True)
        return True

    def reload(self):
        self.screen.clear()
        self.screen.load(self.ids)
        sel = self.view.widget_tree.get_selection()
        if sel.get_mode() == gtk.SELECTION_MULTIPLE:
            sel.select_all()

    def sel_ids_get(self):
        return self.screen.sel_ids_get()

    def destroy(self):
        self.parent.present()
        self.win.destroy()

    def go(self):
        end = False
        limit = self.get_limit()
        offset = self.offset
        if len(self.ids) < limit:
            self.search_count = len(self.ids)
        else:
            self.search_count = rpc.session.rpc_exec_auth_try('/object', 'execute', self.model_name, 'search_count', [], self.context)
        if offset<=0:
            self.but_previous.set_sensitive(False)
        else:
            self.but_previous.set_sensitive(True)

        if offset+limit >= self.search_count:
            self.but_next.set_sensitive(False)
        else:
            self.but_next.set_sensitive(True)
        while not end:
            button = self.win.run()
            if button == gtk.RESPONSE_OK:
                res = self.sel_ids_get() or self.ids
                end = True
            elif button== gtk.RESPONSE_APPLY:
                end = not self.find()
                if end:
                    res = self.sel_ids_get() or self.ids
            else:
                res = None
                end = True
        self.destroy()

        if button== gtk.RESPONSE_ACCEPT:
            dia = dialog(self.model, window=self.parent, domain=self.domain ,context=self.context)
            id = dia.run()
            res = id and [id] or None
            dia.destroy()
        return res

    def search_offset_next(self, button):
        offset = self.offset
        limit = self.get_limit()
        self.offset = offset+limit
        self.find()

    def search_offset_previous(self, button):
        offset = self.offset
        limit = self.get_limit()
        self.offset = (max(offset-limit,0))
        self.find()

    def get_limit(self):
        try:
            return int(self.limit_combo.get_value(self.combo.get_active_iter(), 0))
        except:
            return False
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
