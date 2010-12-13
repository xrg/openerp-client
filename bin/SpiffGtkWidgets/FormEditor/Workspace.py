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
        self.pref_box        = gtk.EventBox()
        self.form            = Target()
        self.element_factory = ElementFactory()
        self.element_view    = ElementView(self.element_factory)
        self.add(self.box)
        self.box.connect('key-press-event',      self._on_box_key_press)
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
        hbox.pack_start(self.pref_box, False)
        hbox.set_spacing(6)
        self.box.add_bg_widget(hbox)
        self.pref_box.set_size_request(200, -1)
        self.selected     = None
        self.mouse_button = None

        # Load built-in widgets.
        for name in sorted(Elements.__all__):
            if name in ('Element', 'Target'):
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


    def _update_widget_prefs(self):
        if self.pref_box.child:
            self.pref_box.remove(self.pref_box.child)
        element = self.selected.get_element()
        if element is None:
            return
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
            self._update_widget_prefs()


    def _on_box_key_press(self, box, event):
        if event.keyval == 65535:  # Backspace
            self.selected.clear()
            self._update_widget_prefs()


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
            x, y   = self._translate_event_coordinates(event)
            target = self.target_at(x, y)
            if target is None:
                return
            element = target.get_element()
            if element is None:
                element = target.get_parent_layout()
                if element is None:
                    return
            x, y = self.translate_coordinates(element, x, y)
            if element.in_resize_area(x, y):
                cursor = gtk.gdk.Cursor(gtk.gdk.BOTTOM_RIGHT_CORNER)
                element.window.set_cursor(cursor)
            else:
                element.window.set_cursor(None)
            return

        # Check whether we are already in a drag operation.
        moving = self.box.get_moving_child()
        if moving and moving.get_data('copy_of'):
            # Strip the coordinates to the parent layout.
            original = moving.get_data('copy_of')
            layout   = original.get_parent_layout()
            alloc    = layout.get_allocation()
            x1, y1   = self._translate_event_coordinates(event)
            x2, y2   = alloc.x + alloc.width, alloc.y + alloc.height
            x2, y2   = layout.translate_coordinates(self.box, x2, y2)

            # Select the bounding target.
            bounding = self.target_at(min(x1, x2), min(y1, y2))
            if bounding and bounding.get_parent_layout() == layout:
                self.select_target(bounding)
            return
        elif moving:
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
            target = self.selected.get_parent_target()
            if target is None:
                return
            element = target.get_element()
            if element is None:
                return

        # Resize the widget?
        x, y               = self._translate_event_coordinates(event)
        widget_x, widget_y = self.translate_coordinates(element, x, y)
        if element.in_resize_area(widget_x, widget_y):
            widget = element.copy()
            alloc  = element.get_allocation()

            # The widget may span over multiple cells. However, we need to
            # highlight the borders of each individual cell, which does not
            # work when a colspan exists. To work around this, we chop the
            # widget into pieces and assemble it by assigning the pieces into
            # individual cells.
            # Get a "screenshot" of the widget.
            #drawable = gtk.gdk.Pixmap(element.window, alloc.width, alloc.height)
            #pixbuf   = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,
            #                          False,
            #                          8,
            #                          alloc.width,
            #                          alloc.height)
            #pixbuf.get_from_drawable(drawable, drawable.get_colormap(),
            #                         0, 0, 0, 0,
            #                         alloc.width, alloc.height)

            # Chop the screenshot into pieces and replace the original
            # widget by the pieces, allowing for highlighting the borders
            # of individual cells.
            #lft, rgt, top, bot = layout.position_of(target)
            #pixbuf.save('screenshot', "jpeg", {"quality":"100"})

            box_x, box_y = element.translate_coordinates(self.box,
                                                         alloc.x,
                                                         alloc.y)
            widget.set_size_request(alloc.width, alloc.height)
            widget.set_data('copy_of', element)
            self.box.add(widget)
            self.box.set_child_position(widget, box_x, box_y)
            self.box.start_resize(widget, x, y, event.time)
            return

        # Start dragging? Remove the widget from the layout and re-add it as
        # a floating child.
        if element.in_drag_area(widget_x, widget_y):
            target = element.get_parent_target()
            target.clear()
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

        # Was an existing widget resized?
        if target and widget and widget.get_data('copy_of'):
            self.box.remove(widget)

            # Find the upper left and lower right targets.
            original = widget.get_data('copy_of')
            layout   = original.get_parent_layout()
            top_lft  = original.get_parent_target()
            bot_rgt  = self.selected or target1

            # Assign the widget to parent layout targets.
            layout.reassign(original, top_lft, bot_rgt)
            self.unselect_target(target)

        # Was a new widget added, or an existing widget moved?
        elif target and widget:
            self.box.remove(widget)
            target.attach(widget)
            self.unselect_target(target)

        # Was a new widget dragged into a non-dropable area?
        elif widget:
            self.box.remove(widget)

        # Was a target clicked?
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
