# -*- coding: UTF-8 -*-
# Copyright (C) 2008 Samuel Abels, http://debain.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import gtk
import pango

class AnnotationView(gtk.EventBox):
    def __init__(self, annotation):
        gtk.EventBox.__init__(self)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK   |
                        gtk.gdk.BUTTON_RELEASE_MASK |
                        gtk.gdk.POINTER_MOTION_MASK |
                        gtk.gdk.POINTER_MOTION_HINT_MASK)
        self.annotation = annotation
        self.buffer     = annotation.buffer
        self.view       = gtk.TextView(self.buffer)
        align           = gtk.Alignment(.5, .5, 1, 1)
        align.set_padding(1, 1, 1, 1)
        align.add(self.view)
        self.add(align)
        self.view.set_wrap_mode(gtk.WRAP_WORD)
        self.view.connect_after('move-cursor', self._on_move_cursor_after)
        self.view.connect('focus-in-event',  self._on_focus_in_event)
        self.view.connect('focus-out-event', self._on_focus_out_event)
        self.buffer.connect('mark-set', self._on_buffer_mark_set)


    def _on_buffer_mark_set(self, buffer, iter, mark):
        if mark.get_name() not in ('selection_bound', 'insert'):
            return
        # Move the mark to the text start.
        if iter.get_offset() < self.annotation.title_len:
            iter = buffer.get_iter_at_offset(self.annotation.title_len)
            buffer.move_mark(mark, iter)


    def _on_focus_in_event(self, text_view, event):
        self.annotation.set_title(self.annotation.get_title(), True)
        self.emit('focus-in-event', event)


    def _on_focus_out_event(self, text_view, event):
        self.annotation.set_title(self.annotation.get_title(), True)
        self.emit('focus-out-event', event)


    def _on_move_cursor_after(self, text_view, step_size, count, extend):
        insert = self.buffer.get_insert()
        iter   = self.buffer.get_iter_at_mark(insert)
        if iter.get_offset() <= self.annotation.title_len:
            iter = self.buffer.get_iter_at_offset(self.annotation.title_len)
            self.buffer.place_cursor(iter)
            return True


    def modify_bg(self, color):
        self.view.modify_base(gtk.STATE_NORMAL, color)


    def modify_border(self, color):
        gtk.EventBox.modify_bg(self, gtk.STATE_NORMAL, color)


    def modify_fg(self, color):
        self.view.modify_fg(gtk.STATE_NORMAL, color)


    def get_border_color(self):
        return self.get_style().bg[gtk.STATE_NORMAL]
