# -*- coding: UTF-8 -*-
# Copyright (C) 2004,2005 by SICEm S.L.
# Copyright (C) 2005 Red Hat, Inc.
# Copyright (C) 2006 Async Open Source
# Copyright (C) 2009 Samuel Abels
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
import gobject, gtk
from gtk import gdk

CHILD_NONE, \
CHILD_MOVE, \
CHILD_RESIZE = range(3)

def set_adjustment_upper(adj, upper, always_emit):
    changed = False
    value_changed = False

    min = max(0.0, upper - adj.page_size)

    if upper != adj.upper:
        adj.upper = upper
        changed = True

    if adj.value > min:
        adj.value = min
        value_changed = True

    if changed or always_emit:
        adj.changed()
    if value_changed:
        adj.value_changed()

def new_adj():
    return gtk.Adjustment(0.0, 0.0, 0.0,
                          0.0, 0.0, 0.0)

class FloatBox(gtk.Container):
    """
    This container does essentially two things:
      - It allows for adding one "normal" child widget. In other words, it
        is very similar to a gtk.EventBox.
      - It also allows for adding floating widgets that are taken out of
        the layout.
    """
    __gsignals__ = dict(set_scroll_adjustments=
                        (gobject.SIGNAL_RUN_LAST, None,
                         (gtk.Adjustment, gtk.Adjustment)))

    def __init__(self, **kwargs):
        """
        Constructor.
        """
        self._evbox                    = gtk.EventBox()
        self._children                 = []
        self._moving_child             = None
        self._moving_start_x_pointer   = 0
        self._moving_start_y_pointer   = 0
        self._moving_start_x_position  = 0
        self._moving_start_y_position  = 0
        self._action_type              = CHILD_NONE
        self._width                    = 100
        self._height                   = 100
        self._hadj                     = None
        self._vadj                     = None
        self._vadj_changed_id          = -1
        self._hadj_changed_id          = -1
        self._bin_window               = None

        gtk.Container.__init__(self)
        self._evbox.set_parent(self)

        if not self._hadj or not self._vadj:
            self._set_adjustments(self._vadj or new_adj(),
                                  self._hadj or new_adj())


    def set_size(self, width, height):
        if self._width != width:
            self._width = width
        if self._height != height:
            self._height = height
        if self._hadj:
            set_adjustment_upper(self._hadj, self._width, False)
        if self._vadj:
            set_adjustment_upper(self._vadj, self._height, False)

        if self.flags() & gtk.REALIZED:
            self._bin_window.resize(max(width, self.allocation.width),
                                    max(height, self.allocation.height))

    def set_child_position(self, child, x, y):
        """
        @param child:
        @param x:
        @param y:
        """
        self._set_child_position(child, x, y)


    def get_moving_child(self):
        return self._moving_child


    def add_bg_widget(self, widget):
        self._evbox.add(widget)


    # Private
    def _set_child_position(self, child, x, y, resize=True):
        if child.x != x or child.y != y:
            child.x, child.y = x, y
            child.compute_size()

            if resize and child.flags() & gtk.VISIBLE:
                self.queue_resize()

    def _get_child_from_widget(self, widget):
        for child in self._children:
            if child.child == widget:
                return child
        else:
            raise AssertionError

    def _pick_child(self, window_x, window_y):
        for child in reversed(self._children):
            x, y = window_x - child.x, window_y - child.y
            if child.in_drag_area(x, y):
                return child
        return None

    def _begin_move_child(self, child, x, y, time):
        if self._moving_child != None:
            raise AssertionError('attempt to move two children at the same time')

        mask = (gdk.BUTTON_PRESS_MASK
              | gdk.BUTTON_RELEASE_MASK
              | gdk.POINTER_MOTION_MASK)
        grab = gdk.pointer_grab(self.window,
                                False,
                                mask,
                                None,
                                None,
                                long(time))
        if grab != gdk.GRAB_SUCCESS:
            raise AssertionError("grab failed")

        self._children.remove(child)
        self._children.append(child)

        alloc = child.get_allocation()
        self._moving_child            = child
        self._moving_start_w          = alloc.width
        self._moving_start_h          = alloc.height
        self._moving_start_x_pointer  = x
        self._moving_start_y_pointer  = y
        self._moving_start_x_position = child.x
        self._moving_start_y_position = child.y

    def _update_move_child(self, x, y):
        child = self._moving_child
        if not child:
            return

        dx = x - self._moving_start_x_pointer
        dy = y - self._moving_start_y_pointer
        if self._action_type == CHILD_MOVE:
            self._set_child_position(child,
                                     self._moving_start_x_position + dx,
                                     self._moving_start_y_position + dy)

        if self._action_type == CHILD_RESIZE:
            child.set_size_request(max(10, self._moving_start_w + dx),
                                   max(10, self._moving_start_h + dy))

            self.queue_draw()

    def _end_move_child(self, time):
        if not self._moving_child:
            return

        gdk.pointer_ungrab(long(time))
        self._moving_child = None

    def _set_adjustments(self, hadj, vadj):
        if not hadj and self._hadj:
            hadj = new_adj()

        if not vadj and self._vadj:
            vadj = new_adj()

        if self._hadj and self._hadj != hadj:
            self._hadj.disconnect(self._hadj_changed_id)

        if self._vadj and self._vadj != vadj:
            self._vadj.disconnect(self._vadj_changed_id)

        need_adjust = False

        if self._hadj != hadj:
            self._hadj = hadj
            set_adjustment_upper(hadj, self._width, False)
            self._hadj_changed_id = hadj.connect(
                "value-changed",
                self._adjustment_changed)
            need_adjust = True

        if self._vadj != vadj:
            self._vadj = vadj
            set_adjustment_upper(vadj, self._height, False)
            self._vadj_changed_id = vadj.connect(
                "value-changed",
                self._adjustment_changed)
            need_adjust = True

        if need_adjust and vadj and hadj:
            self._adjustment_changed()

    def _adjustment_changed(self, adj=None):
        if self.flags() & gtk.REALIZED:
            self._bin_window.move(int(-self._hadj.value),
                                  int(-self._vadj.value))
            self._bin_window.process_updates(True)

    # GtkWidget
    def do_realize(self):
        self.set_flags(gtk.REALIZED)
        self.window = gdk.Window(self.get_parent_window(),
                                 width=self.allocation.width,
                                 height=self.allocation.height,
                                 window_type=gdk.WINDOW_CHILD,
                                 wclass=gdk.INPUT_OUTPUT,
                                 event_mask=(self.get_events() |
                                             gdk.EXPOSURE_MASK))
        self.window.set_user_data(self)
        self.window.move_resize(*self.allocation)

        self._bin_window = gdk.Window(
            self.window,
            window_type=gdk.WINDOW_CHILD,
            x=int(-self._hadj.value),
            y=int(-self._vadj.value),
            width=max(self._width, self.allocation.width),
            height=max(self._height, self.allocation.height),
            colormap=self.get_colormap(),
            wclass=gdk.INPUT_OUTPUT,
            event_mask=(self.get_events() | gdk.EXPOSURE_MASK |
                        gdk.SCROLL_MASK))
        self.style.set_background(self._bin_window, gtk.STATE_NORMAL)
        self._bin_window.set_user_data(self)

        self.set_style(self.style.attach(self.window))

        self._evbox.set_parent_window(self._bin_window)
        for child in self._children:
            child.set_parent_window(self._bin_window)

    def do_unrealize(self):
        self._bin_window.set_user_data(None)
        self._bin_window = None
        self.window.set_user_data(None)

    def do_expose_event(self, event):
        window = event.window

        gc = gdk.GC(window)
        gc.set_rgb_fg_color(self.style.text[self.state])

        self.propagate_expose(self._evbox, event)
        for c in self._children:
            window.draw_rectangle(self.style.base_gc[self.state], True,
                                  c.decoration_x, c.decoration_y,
                                  c.decoration_width, c.decoration_height)
            window.draw_rectangle(gc, False,
                                  c.decoration_x, c.decoration_y,
                                  c.decoration_width, c.decoration_height)

            self.propagate_expose(c, event)

    def do_map(self):
        self.set_flags(gtk.MAPPED)
        flags = self._evbox.flags()
        if flags & gtk.VISIBLE and not flags & gtk.MAPPED:
            self._evbox.map()
        for child in self._children:
            flags = child.flags()
            if flags & gtk.VISIBLE and not flags & gtk.MAPPED:
                child.map()
        self._bin_window.show()
        self.window.show()

    def do_size_request(self, req):
        req.width = 0
        req.height = 0

        self._evbox.size_request()
        req.width, req.height = self._evbox.get_size_request()
        for child in self._children:
            if child.flags() & gtk.VISIBLE:
                child.compute_size()
                req.width = max(req.width,
                                child.decoration_x + child.decoration_width)
                req.height = max(req.height,
                                 child.decoration_y + child.decoration_height)
            child.size_request()

        req.width = req.width + self.border_width * 2
        req.height = req.height + self.border_width * 2

    def do_size_allocate(self, allocation):
        self.allocation = allocation
        if self._evbox.flags() & gtk.VISIBLE:
            self._evbox.size_allocate((0, 0, allocation.width, allocation.height))

        for c in self._children:
            if c.flags() & gtk.VISIBLE:
                w, h = c.get_child_requisition()
                c.size_allocate((c.x, c.y, w, h))

        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)
            self._bin_window.resize(max(self._width, allocation.width),
                                    max(self._height, allocation.height))

        self._hadj.page_size = allocation.width
        self._hadj.page_increment = allocation.width * 0.9
        self._hadj.lower = 0
        set_adjustment_upper(self._hadj,
                             max(allocation.width, self._width), True)

        self._vadj.page_size = allocation.height
        self._vadj.page_increment = allocation.height * 0.9
        self._vadj.lower = 0
        self._vadj.upper = max(allocation.height, self._height)
        set_adjustment_upper(self._vadj,
                             max(allocation.height, self._height), True)

    def do_set_scroll_adjustments(self, hadj, vadj):
        self._set_adjustments(hadj, vadj)

    def do_key_press_event(self, event):
        if event.keyval == gtk.keysyms.Escape:
            self._end_move_child(event.time)

    def _translate_event_coordinates(self, event):
        # Huh. I haven't found any such thing in the gtk API docs, though
        # it seems like a fairly common thing to do.
        my_x, my_y = self.window.get_origin()
        ev_x, ev_y = event.window.get_origin()
        return int(event.x + ev_x - my_x), int(event.y + ev_y - my_y)

    def do_button_press_event(self, event):
        if self._moving_child != None:
            return

        x, y  = self._translate_event_coordinates(event)
        child = self._pick_child(x, y)
        if child == None:
            return

        if child.in_resize_area(x, y):
            self._action_type = CHILD_RESIZE
        else:
            self._action_type = CHILD_MOVE

        self._begin_move_child(child, x, y, event.time)

    def do_button_release_event(self, event):
        x, y = self._translate_event_coordinates(event)
        self._update_move_child(x, y)
        self._end_move_child(event.time)

    def do_motion_notify_event(self, event):
        if self._moving_child is None:
            return
        x, y = self._translate_event_coordinates(event)
        self._update_move_child(x, y)

    # GtkContainer
    def do_forall(self, internals, callback, data):
        callback(self._evbox, data)
        for child in self._children:
            callback(child, data)

    def do_add(self, element):
        self._children.append(element)
        element.set_parent(self)
        element.show_all()

        w, h  = element.size_request()
        alloc = gdk.Rectangle(element.x, element.y, w, h)
        element.size_allocate(alloc)

        if element.flags() & gtk.VISIBLE:
            self.queue_resize()
        self.queue_draw()


    def do_remove(self, element):
        if element == self._evbox:
            element.unparent()
            return

        if self._moving_child == element:
            self._end_move_child(0)

        was_visible = element.flags() & gtk.VISIBLE
        self._children.remove(element)
        element.unparent()

        if was_visible:
            self.queue_resize()
        self.queue_draw()

if gtk.pygtk_version >= (2, 8):
    FloatBox.set_set_scroll_adjustments_signal('set-scroll-adjustments')

gobject.type_register(FloatBox)
