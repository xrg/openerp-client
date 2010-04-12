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
from rpc import RPCProxy

class pager(object):

    DEFAULT_LIMIT = 20

    def __init__(self, object, relation, screen):
        self.object = object
        self.rpc = RPCProxy(relation)
        self.screen = screen
        self.domain = []
        self.type = screen.type

    def create_event_box(self, title, signal, stock_id):
        event_box = gtk.EventBox()
        event_box.set_tooltip_text(title)
        event_box.set_events(gtk.gdk.BUTTON_PRESS)
        event_box.connect('button_press_event', signal)
        img = gtk.Image()
        img.set_from_stock(stock_id, gtk.ICON_SIZE_MENU)
        img.set_alignment(0.5, 0.5)
        event_box.add(img)
        return event_box

    def search_count(self):
        if self.type == 'one2many':
            parent = self.screen.models.parent
            if not (parent and self.screen.models.models):
                return
            if not self.object.parent_field:
                return
            parent_ids = parent.id and [parent.id] or []
            self.domain = [(self.object.parent_field,'in',parent_ids)]
            self.screen.search_count = self.rpc.search_count(self.domain)
        else:
            self.screen.search_count = len(self.object.model.m2m_cache[self.object.name])
        if self.screen.current_model in self.screen.models.models:
            pos = self.screen.models.models.index(self.screen.current_model)
            self.screen.signal('record-message', (pos + self.screen.offset,
                len(self.screen.models.models or []) + self.screen.offset,
                self.screen.search_count, self.screen.current_model.id))

    def get_active_text(self):
        model = self.object.cb.get_model()
        active = self.object.cb.get_active()
        if active < 0:
            return False
        try:
            return int(model[active][0])
        except:
            return False

    def limit_changed(self):
        self.screen.limit = self.get_active_text()
        self.screen.offset = 0
        self.set_models(self.screen.offset, self.screen.limit)

    def set_sensitivity(self):
        offset = self.screen.offset
        limit = self.screen.limit
        total_rec = self.screen.search_count
        try:
            pos = self.screen.models.models.index(self.screen.current_model)
        except:
            pos = -1
        self.object.eb_prev_page.set_sensitive(True)
        self.object.eb_pre.set_sensitive(True)
        self.object.eb_next_page.set_sensitive(True)
        self.object.eb_next.set_sensitive(True)
        self.object.cb.set_sensitive(True)

        if offset <= 0:
            self.object.eb_prev_page.set_sensitive(False)

        if pos <= 0:
            self.object.eb_pre.set_sensitive(False)

        if offset + limit >= total_rec:
            self.object.eb_next_page.set_sensitive(False)

        if self.screen.models.models and \
            pos == len(self.screen.models.models) - 1 or pos < 0:
            self.object.eb_next.set_sensitive(False)

        if not self.screen.models.models:
            self.object.cb.set_sensitive(False)

    def set_models(self, offset=0, limit=DEFAULT_LIMIT):
        if self.type == 'one2many':
            parent = self.screen.models.parent
            ids = self.rpc.search(self.domain, offset, limit)
            if not ids:return
            model_field = parent.mgroup.mfields[self.object.attrs['name']]
            if not limit:
                self.screen.limit = len(ids)
            model_field.limit = limit or len(ids)
            model_field.set(parent, ids)
            self.object.display(parent, model_field)
        else:
            if not limit:
                ids = self.object.model.m2m_cache[self.object.name]
                self.screen.limit = len(ids)
            else:
                ids = self.object.model.m2m_cache[self.object.name][offset:offset + limit]
            model_field = self.object.model_field
            model_field.limit = limit or len(ids)
            self.screen.models.clear()
            self.screen.load(ids)
            self.screen.display()
        self.screen.current_view.set_cursor()
        self.set_sensitivity()

    def next_record(self):
        self.screen.display_next()
        self.set_sensitivity()
        return

    def prev_record(self):
        self.screen.display_prev()
        self.set_sensitivity()
        return

    def next_page(self):
        self.screen.offset = self.screen.offset + self.screen.limit
        self.set_models(self.screen.offset, self.screen.limit)
        return

    def prev_page(self):
        self.screen.offset = max(self.screen.offset - self.screen.limit, 0)
        self.set_models(self.screen.offset, self.screen.limit)
        return

    def reset_pager(self):
        self.screen.offset = 0
        self.screen.limit = self.get_active_text()
        if self.type == 'many2many':
            self.set_models(self.screen.offset, self.screen.limit)
        self.set_sensitivity()
