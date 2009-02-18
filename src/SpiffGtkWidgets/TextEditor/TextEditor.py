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
import gobject, gtk, cairo
from SpiffGtkWidgets import color
from TextBuffer      import TextBuffer
from Layout          import Layout
from AnnotationView  import AnnotationView

class TextEditor(gtk.TextView):
    def __init__(self, textbuffer = None, *args, **kwargs):
        if textbuffer is None:
            textbuffer = TextBuffer()
        gtk.TextView.__init__(self, textbuffer, *args, **kwargs)
        self.buffer           = textbuffer
        self.anno_width       = 200
        self.anno_padding     = 10
        self.anno_layout      = Layout(self)
        self.anno_views       = {}
        self.show_annotations = True
        self.exposed          = False
        self.set_right_margin(50 + self.anno_padding)
        self.connect('expose_event',        self._on_expose_event)
        self.connect('motion-notify-event', self._on_motion_notify_event)
        self.connect('event-after',         self._on_event_after)
        self.buffer.connect('mark-set',           self._on_buffer_mark_set)
        self.buffer.connect('annotation-added',   self._on_annotation_added)
        self.buffer.connect('annotation-removed', self._on_annotation_removed)
        self.set_wrap_mode(gtk.WRAP_WORD)


    def _on_motion_notify_event(self, editor, event):
        x, y = self.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET,
                                            int(event.x),
                                            int(event.y))
        tags = self.get_iter_at_location(x, y).get_tags()

        # Without this call, further motion notify events don't get
        # triggered.
        self.window.get_pointer()

        # If any of the tags are links, show a hand.
        cursor = gtk.gdk.Cursor(gtk.gdk.XTERM)
        for tag in tags:
            if tag.get_data('link'):
                cursor = gtk.gdk.Cursor(gtk.gdk.HAND2)
                break

        self.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(cursor)
        return False


    def _on_event_after(self, textview, event):
        # Handle links here. Only when a button was released.
        if event.type != gtk.gdk.BUTTON_RELEASE:
            return False
        if event.button != 1:
            return False

        # Don't follow a link if the user has selected something.
        bounds = self.buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
            if start.get_offset() != end.get_offset():
                return False

        # Check whether the cursor is pointing at a link.
        x, y = self.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET,
                                            int(event.x),
                                            int(event.y))
        iter = textview.get_iter_at_location(x, y)

        for tag in iter.get_tags():
            link = tag.get_data('link')
            if not link:
                continue
            self.emit('link-clicked', link)
            break
        return False


    def _on_buffer_mark_set(self, buffer, iter, mark):
        self._update_annotations()


    def _on_expose_event(self, widget, event):
        if not self.exposed:
            self.exposed = True
            self._update_annotation_area()
            self._update_annotations()

        text_window = widget.get_window(gtk.TEXT_WINDOW_TEXT)
        if event.window != text_window:
            return

        # Create the cairo context.
        ctx = event.window.cairo_create()

        # Restrict Cairo to the exposed area; avoid extra work
        ctx.rectangle(event.area.x,
                      event.area.y,
                      event.area.width,
                      event.area.height)
        ctx.clip()

        self.draw(ctx, *event.window.get_size())


    def draw(self, ctx, w, h):
        if ctx is None:
            return
        if not self.show_annotations:
            return

        # Draw the dashes that connect annotations to their marker.
        ctx.set_line_width(1)
        ctx.set_dash((3, 2))
        right_margin = self.get_right_margin()
        for annotation in self.anno_layout.get_children():
            mark_x, mark_y = self._get_annotation_mark_position(annotation)
            anno_x, anno_y, anno_w, anno_h, d = annotation.window.get_geometry()
            path = [(mark_x,           mark_y - 5),
                    (mark_x,           mark_y),
                    (w - right_margin, mark_y),
                    (w,                anno_y + anno_h / 2)]

            stroke_color = annotation.get_border_color()
            ctx.set_source_rgba(*color.to_rgba(stroke_color))
            ctx.move_to(*path[0])
            for x, y in path[1:]:
                ctx.line_to(x, y)
            ctx.stroke()


    def _get_annotation_mark_offset(self, view1, view2):
        mark1 = view1.annotation.start_mark
        mark2 = view2.annotation.start_mark
        iter1 = self.get_buffer().get_iter_at_mark(mark1)
        iter2 = self.get_buffer().get_iter_at_mark(mark2)
        rect1 = self.get_iter_location(iter1)
        rect2 = self.get_iter_location(iter2)
        if rect1.y != rect2.y:
            return rect1.y - rect2.y
        return rect2.x - rect1.x


    def _get_annotation_mark_position(self, view):
        start_mark     = view.annotation.start_mark
        iter           = self.get_buffer().get_iter_at_mark(start_mark)
        rect           = self.get_iter_location(iter)
        mark_x, mark_y = rect.x, rect.y + rect.height
        return self.buffer_to_window_coords(gtk.TEXT_WINDOW_TEXT,
                                            mark_x, mark_y)


    def _update_annotation(self, annotation):
        # Resize the annotation.
        item_width = self.anno_width - 2 * self.anno_padding
        annotation.set_size_request(item_width, -1)

        # Find the x, y of the annotation's mark.
        mark_x, mark_y = self._get_annotation_mark_position(annotation)
        self.anno_layout.pull(annotation, mark_y)


    def _update_annotation_area(self):
        # Update the width and color of the annotation area.
        self.set_border_window_size(gtk.TEXT_WINDOW_RIGHT, self.anno_width)
        bg_color = self.get_style().base[gtk.STATE_NORMAL]
        window   = self.get_window(gtk.TEXT_WINDOW_RIGHT)
        if window:
            window.set_background(bg_color)


    def _update_annotations(self):
        if not self.show_annotations:
            return

        # Sort the annotations by line/char number and update them.
        iter   = self.get_buffer().get_end_iter()
        rect   = self.get_iter_location(iter)
        height = rect.y + rect.height
        self.anno_layout.sort(self._get_annotation_mark_offset)
        for annotation in self.anno_layout.get_children():
            self._update_annotation(annotation)
        self.anno_layout.update(self.anno_width, height)

        # Update lines.
        self.queue_draw()


    def set_annotation_area_width(self, width, padding = 10):
        self.anno_width   = width
        self.anno_padding = padding
        self._update_annotations()


    def _on_annotation_added(self, buffer, annotation):
        if self.show_annotations == False:
            return
        annotation.set_display_buffer(self.buffer)
        view = AnnotationView(annotation)
        self.anno_views[annotation] = view
        for event in ('focus-in-event', 'focus-out-event'):
            view.connect(event, self._on_annotation_event, annotation, event)
        view.show_all()
        self._update_annotation_area()
        self.anno_layout.add(view)
        self.add_child_in_window(view,
                                 gtk.TEXT_WINDOW_RIGHT,
                                 self.anno_padding,
                                 0)
        self._update_annotations()


    def _on_annotation_removed(self, buffer, annotation):
        view = self.anno_views[annotation]
        self.anno_layout.remove(view)
        self.remove(view)


    def _on_annotation_event(self, buffer, *args):
        annotation = args[-2]
        event_name = args[-1]
        self.emit('annotation-' + event_name, annotation)


    def set_show_annotations(self, active = True):
        if self.show_annotations == active:
            return

        # Unfortunately gtk.TextView deletes all children from the
        # border window if its size is 0. So we must re-add them when the
        # window reappears.
        self.show_annotations = active
        if active:
            for annotation in self.buffer.get_annotations():
                self._on_annotation_added(self.buffer, annotation)
        else:
            for annotation in self.buffer.get_annotations():
                self._on_annotation_removed(self.buffer, annotation)
            self.set_border_window_size(gtk.TEXT_WINDOW_RIGHT, 0)

gobject.signal_new('link-clicked',
                   TextEditor,
                   gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_PYOBJECT, ))

gobject.signal_new('annotation-focus-in-event',
                   TextEditor,
                   gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_PYOBJECT, ))

gobject.signal_new('annotation-focus-out-event',
                   TextEditor,
                   gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_PYOBJECT, ))
