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
import parser
import observator


class EditableTreeView(gtk.TreeView, observator.Observable):

    leaving_model_events = (gtk.keysyms.Up, gtk.keysyms.Down,
                            gtk.keysyms.Return, gtk.keysyms.KP_Enter)
    leaving_events = leaving_model_events + (gtk.keysyms.Tab,
                                             gtk.keysyms.ISO_Left_Tab) 

    def __init__(self, position):
        super(EditableTreeView, self).__init__()
        self.editable = position
        self.cells = {}

    def on_quit_cell(self, current_model, fieldname, value):
        modelfield = current_model[fieldname]
        if hasattr(modelfield, 'editabletree_entry'):
            del modelfield.editabletree_entry
        cell = self.cells[fieldname]

        # The value has not changed ... do nothing.
        if value == cell.get_textual_value(current_model):
            return

        try:
            real_value = cell.value_from_text(current_model, value)
            modelfield.set_client(current_model, real_value)
        except parser.UnsettableColumn:
            return

        # And now the on_change stuff ... only 3 lines are enough.
        #callback = modelfield.attrs.get('on_change', '')
        #if callback:
        #   current_model.on_change(callback)

        # And finally the conditional default
        #if modelfield.attrs.get('change_default', False):
        #   current_model.cond_default(fieldname, real_value)

    def on_open_remote(self, current_model, fieldname, create, value):
        modelfield = current_model[fieldname]
        cell = self.cells[fieldname]
        if value != cell.get_textual_value(current_model) or not value:
            changed = True
        else:
            changed=False
        try:
            valid, value = cell.open_remote(current_model, create, changed, value)
            if valid:
                modelfield.set_client(current_model, value)
        except NotImplementedError:
            pass
        return cell.get_textual_value(current_model)

    def on_create_line(self):
        model = self.get_model()
        if self.editable == 'top':
            method = model.prepend
        else:
            method = model.append
        ctx=self.screen.context.copy()
        if self.screen.current_model.parent:
            ctx.update(self.screen.current_model.parent.expr_eval(self.screen.default_get))
        new_model = model.model_group.model_new(domain=self.screen.domain, context=ctx)
        res = method(new_model)
        return res


    # if changed, please update the corresponded method in the DecoratedTreeView class
    def get_columns(self, include_non_visible=True, include_non_editable=True):
        def column_is_editable(column):
            renderer = column.get_cell_renderers()[0]
            if isinstance(renderer, gtk.CellRendererToggle):
                return renderer.get_property('activatable')
            else:
                return renderer.get_property('editable')
        
        columns = super(EditableTreeView, self).get_columns()
        if not include_non_visible:
            columns = filter(lambda c: c.get_visible(), columns)
        if not include_non_editable:
            columns = filter(lambda c: column_is_editable(c), columns)
        return columns


    def __next_column(self, col):
        cols = self.get_columns(False, False)
        current = cols.index(col)
        idx = (current + 1) % len(cols)
        return cols[idx]

    def __prev_column(self, col):
        cols = self.get_columns(False, False)
        current = cols.index(col)
        idx = (current - 1) % len(cols)
        return cols[idx]

    def set_cursor(self, path, focus_column=None, start_editing=False):
        if focus_column and (focus_column._type in ('many2one','many2many')):
            msg = _('Shortcut: %s') % ('<i>%s</i>' % _('F1 New - F2 Open/Search'))
            self.warn('misc-message', msg)
        elif focus_column and (focus_column._type in ('boolean')):
            start_editing=False
        else:
            self.warn('misc-message', '')
        return super(EditableTreeView, self).set_cursor(path, focus_column,
                start_editing)

    def set_value(self):
        path, column = self.get_cursor()
        store = self.get_model()
        if not path or not column:
            return True
        model = store.get_value(store.get_iter(path), 0)
        modelfield = model[column.name]
        if hasattr(modelfield, 'editabletree_entry'):
            entry = modelfield.editabletree_entry
            if isinstance(entry, gtk.Entry):
                txt = entry.get_text()
            else:
                txt = entry.get_active_text()
            self.on_quit_cell(model, column.name, txt)
        return True

    def on_keypressed(self, entry, event):
        path, column = self.get_cursor()
        store = self.get_model()
        model = store.get_value(store.get_iter(path), 0)
        if event.keyval in self.leaving_events:
            shift_pressed = bool(gtk.gdk.SHIFT_MASK & event.state)
            if isinstance(entry, gtk.Entry):
                txt = entry.get_text()
            elif isinstance(entry, gtk.ComboBoxEntry) and shift_pressed and event.keyval != gtk.keysyms.ISO_Left_Tab:
                model = entry.get_property('model')
                txt = entry.get_active_text()
                for idx, line in enumerate(model):
                    if line[1] == txt:
                        break
                if event.keyval == gtk.keysyms.Up:
                    entry.set_active((idx - 1) % len(model))
                elif event.keyval == gtk.keysyms.Down:
                    entry.set_active((idx + 1) % len(model))
                return True
            else:
                txt = entry.get_active_text()
            entry.disconnect(entry.editing_done_id)
            self.on_quit_cell(model, column.name, txt)
            entry.editing_done_id = entry.connect('editing_done', self.on_editing_done)
        if event.keyval in self.leaving_model_events:
            if model.validate() and self.screen.tree_saves:
                id = model.save()
                if not id:
                    return True
                else:
                    res = store.saved(id)
                    if res:
                        self.screen.display(res.id)

            elif self.screen.tree_saves:
                invalid_fields = model.invalid_fields
                for col in self.get_columns():
                    if col.name in invalid_fields:
                        break
                self.set_cursor(path, col, True)
                msg = _('Warning; field %s is required!') % ('<b>%s</b>' % invalid_fields[col.name]) 
                self.warn('misc-message', msg, "red")
                return True

        if event.keyval == gtk.keysyms.Tab:
            new_col = self.__next_column(column)
            self.set_cursor(path, new_col, True)
        elif event.keyval == gtk.keysyms.ISO_Left_Tab:
            new_col = self.__prev_column(column)
            self.set_cursor(path, new_col, True)
        elif event.keyval == gtk.keysyms.Up:
            self._key_up(path, store, column)
        elif event.keyval == gtk.keysyms.Down:
            self._key_down(path,store,column)
        elif event.keyval in (gtk.keysyms.Return, gtk.keysyms.KP_Enter):
            if self.editable == 'top':
                new_path = self._key_up(path, store, column)
            else:
                new_path = self._key_down(path,store,column)
            col = self.get_columns(False, False)[0]
            self.set_cursor(new_path, col, True)
        elif event.keyval == gtk.keysyms.Escape:
            if model.id is None:
                store.remove(store.get_iter(path))
                self.screen.current_model = False
            if not path[0]:
                self.screen.current_model = False
            self.screen.display()
            self.set_cursor(path, column, False)
        elif event.keyval in (gtk.keysyms.F1, gtk.keysyms.F2):
            if (column._type not in ('many2one','many2many')):
                return True
            if isinstance(entry, gtk.Entry):
                value=entry.get_text()
            else:
                value=entry.get_active_text()
            entry.disconnect(entry.editing_done_id)
            newval = self.on_open_remote(model, column.name,
                                create=(event.keyval==gtk.keysyms.F1), value=value)
            if isinstance(entry, gtk.Entry):
                entry.set_text(newval)
            else:
                entry.set_active_text(newval)
            entry.editing_done_id = entry.connect('editing_done', self.on_editing_done)
            self.set_cursor(path, column, True)
            return False
        else:
            modelfield = model[column.name]
            if isinstance(entry, gtk.Entry):
                entry.set_max_length(int(modelfield.attrs.get('size', 0)))
            # store in the model the entry widget to get the value in set_value
            modelfield.editabletree_entry = entry
            model.modified = True
            model.modified_fields.setdefault(column.name)
            return False

        return True

    def _key_down(self, path, store, column):
        if path[0] == len(store) - 1 and self.editable == 'bottom':
            self.on_create_line()
        new_path = (path[0] + 1) % len(store)
        self.set_cursor(new_path, column, True)
        return new_path

    def _key_up(self, path, store, column):
        if path[0] == 0 and self.editable == 'top':
            self.on_create_line()
            new_path = 0
        else:
            new_path = (path[0] - 1) % len(store)
        self.set_cursor(new_path, column, True)
        return new_path

    def on_editing_done(self, entry):
        path, column = self.get_cursor()
        if not path:
            return True
        store = self.get_model()
        model = store.get_value(store.get_iter(path), 0)
        if isinstance(entry, gtk.Entry):
            self.on_quit_cell(model, column.name, entry.get_text())
        elif isinstance(entry, gtk.ComboBoxEntry):
            self.on_quit_cell(model, column.name, entry.get_active_text())


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

