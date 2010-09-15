# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from interface import parser_view

class ViewGallery(parser_view):

    def __init__(self, window, screen, widget, children=None, state_aware_widgets=None, toolbar=None, submenu=None, help=None):
        super(ViewGallery, self).__init__(window, screen, widget, children, state_aware_widgets, toolbar, submenu)
        self.view_type = 'gallery'
        self.model_add_new = False
        self.view = widget
        self.screen = screen
        self.reload = False

        self.widget = widget.widget
        self.widget.screen = screen
        self.widget.connect_after('item-activated', self.__sig_switch)
        self.widget.connect('selection-changed', self.__sig_select_changed)
        self.display()

    def cancel(self):
        pass

    def __str__(self):
        return 'ViewGallery (%s)' % self.screen.resource

    def __getitem__(self, name):
        return None

    def destroy(self):
        self.widget.destroy()
        del self.screen
        del self.widget

    def set_value(self):
        return True

    def reset(self):
        pass

    def display(self):
        do_reload = False
        if self.reload \
            or (not self.widget.get_model()) \
            or self.screen.models <> self.widget.get_model().model_group:
            do_reload = True

        self.view.display(self.screen, do_reload)

        self.reload = False

    def signal_record_changed(self, signal0, models, signal1, *args):
        self.reload = True

    def sel_ids_get(self):
        def _func_sel_get(iconview, path, ids):
            model = iconview.get_model()
            iter = model.get_iter(path)
            ids.append(model.get_value(iter, 0).id)
        ids = []
        sel = self.widget.get_selected_items()
        if sel:
            self.widget.selected_foreach(_func_sel_get, ids)
        return ids

    def sel_models_get(self):
        def _func_model_get(iconview, path, models):
            model = iconview.get_model()
            iter = model.get_iter(path)
            models.append(model.get_value(iter, 0))
        models = []
        sel = self.widget.get_selected_items()
        if sel:
            self.widget.selected_foreach(_func_model_get, models)
        return models

    def on_change(self, callback):
        pass

    def unset_editable(self):
        pass

    def set_cursor(self, new=False):
        self.view.set_cursor(self.screen)

    def __sig_switch(self, iconview, *args):
        self.screen.row_activate(self.screen)

    def __sig_select_changed(self, iconview):
        model = iconview.get_model()
        if not model:
            return
        selpaths = iconview.get_selected_items()
        if len(selpaths):
            # at least one item selected
            # update screen current_model with the first selected
            path_iter = model.get_iter(selpaths[0][0])
            data = model.get_value(path_iter, 0)
            self.screen.current_model = data

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

