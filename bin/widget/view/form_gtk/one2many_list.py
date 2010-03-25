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

import gobject
import gtk

import gettext

import common
from common import sur
import wid_common

import interface
from widget.screen import Screen
from pager import pager
import service
import tools


class dialog(object):
    def __init__(self, model_name, parent, model=None, attrs=None, model_ctx=None,
            window=None, default_get_ctx=None, readonly=False):

        if attrs is None:
            attrs = {}
        if model_ctx is None:
            model_ctx = {}
        if default_get_ctx is None:
            default_get_ctx = {}

        if not window:
            window = service.LocalService('gui.main').window

        self.dia = gtk.Dialog(_('OpenERP - Link'), window,
                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT)
        self.window = window
        if ('string' in attrs) and attrs['string']:
            self.dia.set_title(self.dia.get_title() + ' - ' + attrs['string'])
        self.dia.set_property('default-width', 760)
        self.dia.set_property('default-height', 500)
        self.dia.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.dia.set_icon(common.OPENERP_ICON)

        self.accel_group = gtk.AccelGroup()
        self.dia.add_accel_group(self.accel_group)

        self.but_cancel = self.dia.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CANCEL)
        self.but_cancel.add_accelerator('clicked', self.accel_group, gtk.keysyms.Escape, gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

        self.but_ok = self.dia.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        self.but_ok.add_accelerator('clicked', self.accel_group, gtk.keysyms.Return, gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

        self.default_get_ctx = default_get_ctx

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_placement(gtk.CORNER_TOP_LEFT)
        scroll.set_shadow_type(gtk.SHADOW_NONE)
        self.dia.vbox.pack_start(scroll, expand=True, fill=True)

        vp = gtk.Viewport()
        vp.set_shadow_type(gtk.SHADOW_NONE)
        scroll.add(vp)

        self.screen = Screen(model_name, view_type=[], parent=parent, window=self.dia, readonly=readonly)
        self.screen.models._context.update(model_ctx)
        if not model:
            model = self.screen.new(context=default_get_ctx)
        else:
            self.screen.models.model_add(model)
        self.screen.current_model = model
        if ('views' in attrs) and ('form' in attrs['views']):
            arch = attrs['views']['form']['arch']
            fields = attrs['views']['form']['fields']
            self.screen.add_view(arch, fields, display=True,
                    context=default_get_ctx)
        else:
            self.screen.add_view_id(False, 'form', display=True,
                    context=default_get_ctx)
        vp.add(self.screen.widget)
        x,y = self.screen.screen_container.size_get()
        vp.set_size_request(x,y+30)
        self.dia.show_all()
        self.screen.readonly = readonly
        self.screen.display()

    def new(self):
        model = self.screen.new(context=self.default_get_ctx)
        self.screen.models.model_add(model)
        self.screen.current_model = model
        return True

    def run(self, datas={}):
        end = False
        while not end:
            res = self.dia.run()
            end = (res != gtk.RESPONSE_OK) or self.screen.current_model.validate()
            if not end:
                self.screen.display()

        if res==gtk.RESPONSE_OK:
            self.screen.current_view.set_value()
            model = self.screen.current_model
            return (True, model)
        return (False, False)

    def destroy(self):
        self.screen.signal_unconnect(self)
        self.window.present()
        self.dia.destroy()
        self.screen.destroy()


class one2many_list(interface.widget_interface):
    def __init__(self, window, parent, model, attrs={}):
        interface.widget_interface.__init__(self, window, parent, model, attrs)
        self.parent_field = attrs.get('parent_field', False)
        self.context = tools.expr_eval(attrs['context'] or "{}")
        self._readonly = self.default_readonly
        self.widget = gtk.VBox(homogeneous=False, spacing=5)
        hb = gtk.HBox(homogeneous=False, spacing=5)
        menubar = gtk.MenuBar()
        if hasattr(menubar, 'set_pack_direction') and \
                hasattr(menubar, 'set_child_pack_direction'):
            menubar.set_pack_direction(gtk.PACK_DIRECTION_LTR)
            menubar.set_child_pack_direction(gtk.PACK_DIRECTION_LTR)

        menuitem_title = gtk.ImageMenuItem(stock_id='gtk-preferences')

        menu_title = gtk.Menu()
        menuitem_set_to_default = gtk.MenuItem(_('Set to default value'), True)
        menuitem_set_to_default.connect('activate', lambda *x:self._menu_sig_default_get())
        menu_title.add(menuitem_set_to_default)
        menuitem_set_default = gtk.MenuItem(_('Set Default'), True)
        menuitem_set_default.connect('activate', lambda *x: self._menu_sig_default_set())
        menu_title.add(menuitem_set_default)
        menuitem_title.set_submenu(menu_title)

        menubar.add(menuitem_title)
        hb.pack_start(menubar, expand=True, fill=True)

        tooltips = gtk.Tooltips()

        self.eb_new = gtk.EventBox()
        tooltips.set_tip(self.eb_new, _('Create a new entry'))
        self.eb_new.set_events(gtk.gdk.BUTTON_PRESS)
        self.eb_new.connect('button_press_event', self._sig_new)
        img_new = gtk.Image()
        img_new.set_from_stock('gtk-new', gtk.ICON_SIZE_MENU)
        img_new.set_alignment(0.5, 0.5)
        self.eb_new.add(img_new)
        hb.pack_start(self.eb_new, expand=False, fill=False)

        self.eb_open = gtk.EventBox()
        tooltips.set_tip(self.eb_open, _('Edit this entry'))
        self.eb_open.set_events(gtk.gdk.BUTTON_PRESS)
        self.eb_open.connect('button_press_event', self._sig_edit)
        img_open = gtk.Image()
        img_open.set_from_stock('gtk-open', gtk.ICON_SIZE_MENU)
        img_open.set_alignment(0.5, 0.5)
        self.eb_open.add(img_open)
        hb.pack_start(self.eb_open, expand=False, fill=False)

        self.eb_del = gtk.EventBox()
        tooltips.set_tip(self.eb_del, _('Remove this entry'))
        self.eb_del.set_events(gtk.gdk.BUTTON_PRESS)
        self.eb_del.connect('button_press_event', self._sig_remove)
        img_del = gtk.Image()
        img_del.set_from_stock('gtk-delete', gtk.ICON_SIZE_MENU)
        img_del.set_alignment(0.5, 0.5)
        self.eb_del.add(img_del)
        hb.pack_start(self.eb_del, expand=False, fill=False)

        hb.pack_start(gtk.VSeparator(), expand=False, fill=True)
     # Previous Page
        self.eb_prev_page = gtk.EventBox()
        tooltips.set_tip(self.eb_prev_page, _('Previous Page'))
        self.eb_prev_page.set_events(gtk.gdk.BUTTON_PRESS)
        self.eb_prev_page.connect('button_press_event', self._sig_prev_page)
        img_first = gtk.Image()
        img_first.set_from_stock('gtk-goto-first', gtk.ICON_SIZE_MENU)
        img_first.set_alignment(0.5, 0.5)
        self.eb_prev_page.add(img_first)
        hb.pack_start(self.eb_prev_page, expand=False, fill=False)

        self.eb_pre = gtk.EventBox()
        tooltips.set_tip(self.eb_pre, _('Previous Record'))
        self.eb_pre.set_events(gtk.gdk.BUTTON_PRESS)
        self.eb_pre.connect('button_press_event', self._sig_previous)
        img_pre = gtk.Image()
        img_pre.set_from_stock('gtk-go-back', gtk.ICON_SIZE_MENU)
        img_pre.set_alignment(0.5, 0.5)
        self.eb_pre.add(img_pre)
        hb.pack_start(self.eb_pre, expand=False, fill=False)

        self.label = gtk.Label('(0,0)')
        hb.pack_start(self.label, expand=False, fill=False)

        self.eb_next = gtk.EventBox()
        tooltips.set_tip(self.eb_next, _('Next Record'))
        self.eb_next.set_events(gtk.gdk.BUTTON_PRESS)
        self.eb_next.connect('button_press_event', self._sig_next)
        img_next = gtk.Image()
        img_next.set_from_stock('gtk-go-forward', gtk.ICON_SIZE_MENU)
        img_next.set_alignment(0.5, 0.5)
        self.eb_next.add(img_next)
        hb.pack_start(self.eb_next, expand=False, fill=False)

        # Next Page
        self.eb_next_page = gtk.EventBox()
        tooltips.set_tip(self.eb_next_page, _('Next Page'))
        self.eb_next_page.set_events(gtk.gdk.BUTTON_PRESS)
        self.eb_next_page.connect('button_press_event', self._sig_next_page)
        img_last = gtk.Image()
        img_last.set_from_stock('gtk-goto-last', gtk.ICON_SIZE_MENU)
        img_last.set_alignment(0.5, 0.5)
        self.eb_next_page.add(img_last)
        hb.pack_start(self.eb_next_page, expand=False, fill=False)

        hb.pack_start(gtk.VSeparator(), expand=False, fill=True)

        eb_switch = gtk.EventBox()
        tooltips.set_tip(eb_switch, _('Switch'))
        eb_switch.set_events(gtk.gdk.BUTTON_PRESS)
        eb_switch.connect('button_press_event', self.switch_view)
        img_switch = gtk.Image()
        img_switch.set_from_stock('gtk-justify-left', gtk.ICON_SIZE_MENU)
        img_switch.set_alignment(0.5, 0.5)
        eb_switch.add(img_switch)
        hb.pack_start(eb_switch, expand=False, fill=False)

        hb.pack_start(gtk.VSeparator(), expand=False, fill=True)

          # Limit Combo
        self.cb = gtk.combo_box_new_text()
        for limit in ['20','40','80','100']:
            self.cb.append_text(limit)
        self.cb.set_active(0)
        tooltips.set_tip(self.cb, _('Choose Limit'))
        self.cb.connect('changed', self.limit_changed)
        hb.pack_start(self.cb, expand=False, fill=False)

        tooltips.enable()
        self.widget.pack_start(hb, expand=False, fill=True)
        self.screen = Screen(attrs['relation'], view_type=attrs.get('mode','tree,form').split(','), parent=self.parent, views_preload=attrs.get('views', {}), tree_saves=attrs.get('saves', False), create_new=True, row_activate=self._on_activate, default_get=attrs.get('default_get', {}), window=self._window, readonly=self._readonly, limit=20)
        self.screen.type = 'one2many'
        if self.context.get('group_by',False):
            self.context['group_by'] = [self.context['group_by']]
        self.screen.context.update(self.context)
        self.screen.signal_connect(self, 'record-message', self._sig_label)
        menuitem_title.get_child().set_markup('<b>'+self.screen.current_view.title.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')+'</b>')
        self.widget.pack_start(self.screen.widget, expand=True, fill=True)
        self.screen.widget.connect('key_press_event', self.on_keypress)
        self.pager = pager(object=self, relation=attrs['relation'], screen=self.screen)

    def on_keypress(self, widget, event):
        if (not self._readonly) and ((event.keyval in (gtk.keysyms.N, gtk.keysyms.n) and event.state & gtk.gdk.CONTROL_MASK\
            and event.state & gtk.gdk.SHIFT_MASK)):
            self._sig_new(widget, event)
            return False
        if event.keyval in (gtk.keysyms.E, gtk.keysyms.e) and event.state & gtk.gdk.CONTROL_MASK\
            and event.state & gtk.gdk.SHIFT_MASK:
            self._sig_edit(widget, event)
            return False
        if event.keyval in (gtk.keysyms.L, gtk.keysyms.l) and event.state & gtk.gdk.CONTROL_MASK\
            and event.state & gtk.gdk.SHIFT_MASK:
            self.switch_view(widget, event)
            return False

    def destroy(self):
        self.screen.destroy()

    def _on_activate(self, screen, *args):
        self._sig_edit()

    def click_and_action(self, type):
        pos = self.tree_view.pos_get()
        if pos!=None:
            val = self._value[pos]
            id = val.get('id', False)
            obj = service.LocalService('action.main')
            res = obj.exec_keyword(type, {'model':self.model, 'id': id or False, 'ids':[id], 'report_type': 'pdf'})
            return True
        else:
            common.message(_('You have to select a resource !'))
            return False

    def switch_view(self, btn, arg):
        self.screen.switch_view()

    def _readonly_set(self, value):
        self._readonly = value
        self.eb_new.set_sensitive(not value)
        self.eb_del.set_sensitive(not value)
        self.screen.readonly = value
        self.screen.display()

    def _sig_new(self, *args):
        _, event = args
        ctx = self._view.model.expr_eval(self.screen.default_get)
        ctx.update(self._view.model.expr_eval('dict(%s)' % self.attrs.get('context', '')))
        if event.type in (gtk.gdk.BUTTON_PRESS, gtk.gdk.KEY_PRESS):
            if (self.screen.current_view.view_type=='form') or self.screen.editable_get():
                self.screen.new(context=ctx)
                self._readonly = False
                self.screen.current_view.widget.set_sensitive(True)
            else:
                ok = 1
                dia = dialog(self.attrs['relation'], parent=self._view.model, attrs=self.attrs, model_ctx=self.screen.models._context, default_get_ctx=ctx, window=self._window, readonly=self._readonly)
                while ok:
                    ok, value = dia.run()
                    if ok:
                        self.screen.models.model_add(value)
                        value.signal('record-changed', value.parent)
                        self.screen.display()
                        dia.new()
                self.pager.reset_pager()
                dia.destroy()

    def _sig_edit(self, *args):
        if self.screen.current_model:
            dia = dialog(self.attrs['relation'], parent=self._view.model,  model=self.screen.current_model, attrs=self.attrs, window=self._window, readonly=self._readonly)
            ok, value = dia.run()
            dia.destroy()

    def limit_changed(self,*args):
        self.pager.limit_changed()

    def _sig_prev_page(self, *args):
        self.pager.prev_page()

    def _sig_next_page(self, *args):
        self.pager.next_page()

    def _sig_next(self, *args):
        _, event = args
        if event.type == gtk.gdk.BUTTON_PRESS:
            self.pager.next_record()

    def _sig_previous(self, *args):
        _, event = args
        if event.type == gtk.gdk.BUTTON_PRESS:
            self.pager.prev_record()

    def _sig_remove(self, *args):
        _, event = args
        if event.type == gtk.gdk.BUTTON_PRESS:
            if self.screen.current_view.view_type == 'form':
                msg = 'Are you sure to remove this record ?'
            else:
                msg = 'Are you sure to remove those records ?'
            if common.sur(msg):
                    self.screen.remove()
                    self.pager.reset_pager()
                    if not self.screen.models.models:
                        self.screen.current_view.widget.set_sensitive(False)

    def _sig_label(self, screen, signal_data):
        name = '_'
        if signal_data[0] >= 0:
            name = str(signal_data[0] + 1)
        line = '(%s/%s of %s)' % (name, signal_data[1], signal_data[2])
        self.label.set_text(line)

    def _sig_refresh(self, *args):
        pass

    def _sig_sequence(self, *args):
        pass

    def display(self, model, model_field):
        if not model_field:
            self.screen.current_model = None
            self.screen.display()
            return False
        self.pager.search_count()
        self.pager.set_sensitivity()
        super(one2many_list, self).display(model, model_field)
        new_models = model_field.get_client(model)
        if self.screen.models != new_models:
            self.screen.models_set(new_models)
            if (self.screen.current_view.view_type=='tree') and self.screen.editable_get():
                self.screen.current_model = None
        self.screen.display()
        return True

    def set_value(self, model, model_field):
        self.screen.current_view.set_value()
        if self.screen.is_modified():
            model.modified = True
            model.modified_fields.setdefault(model_field.name)
        return True

    def grab_focus(self):
        return self.screen.widget.grab_focus()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

