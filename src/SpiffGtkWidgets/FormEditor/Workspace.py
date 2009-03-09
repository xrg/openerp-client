# Copyright (C) 2009 Samuel Abels <http://debain.org>
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
import gobject, gtk
from FloatBox       import FloatBox
from ElementFactory import ElementFactory
from ElementView    import ElementView
from Elements       import *
import Elements

class Workspace(gtk.EventBox):
    def __init__(self):
        gtk.EventBox.__init__(self)
        self.box             = FloatBox()
        self.pref_vbox       = gtk.VBox()
        self.pref_box        = gtk.EventBox()
        self.form            = Target()
        self.element_factory = ElementFactory()
        self.element_view    = ElementView(self.element_factory)
        self.add(self.box)
        self.box.connect('motion-notify-event',  self._on_box_motion_notify)
        self.box.connect('button-press-event',   self._on_box_button_press)
        self.box.connect('button-release-event', self._on_box_button_release)
        self.element_view.connect('element-button-press-event',
                                  self._on_element_button_press_event)

        hbox = gtk.HBox()
        vbox = gtk.VBox()
        vbox.pack_start(self.element_view, False)
        hbox.pack_start(vbox, False)
        hbox.pack_start(self.form)
        hbox.pack_start(self.pref_vbox, False)
        self.pref_vbox.pack_start(self.pref_box, False)
        hbox.set_spacing(6)
        self.box.add_bg_widget(hbox)
        self.pref_box.set_size_request(200, -1)
        self.selected     = None
        self.mouse_button = None

        # Load built-in widgets.
        for name in sorted(Elements.__all__):
            if name in ('Target'):
                continue
            element_class = Elements.__dict__[name]
            if type(element_class) != gobject.GObjectMeta:
                continue
            self.element_factory.register(element_class)


    def clear(self):
        self.form.clear()


    def target_at(self, x, y):
        x, y = self.box.translate_coordinates(self.form, int(x), int(y))
        return self.form.target_at(x, y)


    def unselect_target(self, target):
        self.selected = None
        target.unselect()


    def _load_pref_widget(self, target):
        if self.pref_box.child is not None:
            self.pref_box.remove(self.pref_box.child)
        if target.get_element() is None:
            return
        element     = target.get_element()
        pref_widget = element.get_pref_widget()
        if pref_widget is None:
            return
        self.pref_box.add(pref_widget)
        self.pref_box.show_all()


    def select_target(self, target):
        if target == self.selected:
            return
        if self.selected:
            self.selected.unselect()
        self.selected = target
        if target is not None:
            target.select()
            self._load_pref_widget(target)


    def _translate_event_coordinates(self, event):
        # Huh. I haven't found any such thing in the gtk API docs, though
        # it seems like a fairly common thing to do.
        my_x, my_y = self.window.get_origin()
        ev_x, ev_y = event.window.get_origin()
        return int(event.x + ev_x - my_x), int(event.y + ev_y - my_y)


    def _on_box_button_press(self, box, event):
        if event.button != 1:
            return
        self.mouse_button = event.button

        # Fetch the widget at the location of the mouse pointer.
        x, y   = self._translate_event_coordinates(event)
        target = self.target_at(x, y)
        if target is not None:
            self.select_target(target)


    def _on_box_motion_notify(self, box, event):
        if self.mouse_button != 1:
            return

        # Check whether we are already in a drag operation.
        if self.box.get_moving_child():
            x, y   = self._translate_event_coordinates(event)
            target = self.target_at(x, y)
            if target is None:
                return
            self.select_target(target)
            return

        # Ending up here, it is time to start a drag operation.
        if not self.selected:
            return
        element = self.selected.get_element()
        if element is None:
            return

        # Resize the widget?
        x, y               = self._translate_event_coordinates(event)
        widget_x, widget_y = self.translate_coordinates(element, x, y)
        if element.in_resize_area(widget_x, widget_y):
            print "Resize start"
            return

        # Start dragging? Remove the widget from the layout and re-add it as
        # a floating child.
        if element.in_drag_area(widget_x, widget_y):
            self.selected.clear()
            self.box.add(element)
            self.box.set_child_position(element, x - 2, y - 4)
            self.box.start_drag(element, x, y, event.time)


    def _on_box_button_release(self, box, event):
        if event.button != 1:
            return
        self.mouse_button = None

        x, y   = self._translate_event_coordinates(event)
        target = self.target_at(x, y)
        widget = self.box.get_moving_child()
        if target and widget:
            self.box.remove(widget)
            target.attach(widget)
            self.unselect_target(target)
        elif widget:
            self.box.remove(widget)
        elif target:
            self.select_target(target)


    def _emit_box_event(self, event):
        # Fake an event such that the FloatBox can pick up the newly
        # created widget.
        x, y         = self.box._translate_event_coordinates(event)
        event.window = self.box.window
        event.x      = float(x)
        event.y      = float(y)
        gtk.main_do_event(event)


    def _on_element_button_press_event(self, view, button, event):
        alloc   = button.get_allocation()
        element = self.element_factory.create(button.get_name())
        element.set_size_request(alloc.width, alloc.height)
        self.box.add(element)
        self.box.set_child_position(element, alloc.x, alloc.y)
        self._emit_box_event(event)
