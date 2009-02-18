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
import sys, os.path, pango
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
import gtk, gtkspell, locale
from SpiffGtkWidgets.TextEditor import TextEditor, Annotation

class Window(gtk.Window):
    n_annotations = 0

    def __init__(self):
        gtk.Window.__init__(self)
        self.vbox   = gtk.VBox()
        self.hbox   = gtk.HBox()
        self.scroll = gtk.ScrolledWindow()
        self.view   = TextEditor()
        buffer      = self.view.get_buffer()
        self.view.modify_font(pango.FontDescription("Arial 12"))
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.set_size_request(800, 600)
        self.vbox.set_border_width(6)
        self.vbox.set_spacing(6)
        self.hbox.set_spacing(6)
        buffer.connect('undo-stack-changed',
                       self._on_buffer_undo_stack_changed)
        self.view.connect('link-clicked', self._on_link_clicked)
        self.view.connect('annotation-focus-out-event',
                          self._on_annotation_focus_out_event)

        # Format changing buttons.
        button = gtk.Button(stock = gtk.STOCK_BOLD)
        button.set_properties(can_focus = False)
        button.connect('clicked',
                       self._on_button_format_clicked,
                       buffer,
                       'bold')
        self.hbox.pack_start(button, False)

        button = gtk.Button(stock = gtk.STOCK_ITALIC)
        button.set_properties(can_focus = False)
        button.connect('clicked',
                       self._on_button_format_clicked,
                       buffer,
                       'italic')
        self.hbox.pack_start(button, False)

        button = gtk.Button(stock = gtk.STOCK_UNDERLINE)
        button.set_properties(can_focus = False)
        button.connect('clicked',
                       self._on_button_format_clicked,
                       buffer,
                       'underline')
        self.hbox.pack_start(button, False)

        # Undo/redo buttons.
        self.undo_button = gtk.Button(stock = gtk.STOCK_UNDO)
        self.undo_button.set_properties(can_focus = False)
        self.undo_button.set_sensitive(buffer.can_undo())
        self.undo_button.connect('clicked', self._on_button_undo_clicked, buffer)
        self.hbox.pack_start(self.undo_button, False)

        self.redo_button = gtk.Button(stock = gtk.STOCK_REDO)
        self.redo_button.set_properties(can_focus = False)
        self.redo_button.set_sensitive(buffer.can_redo())
        self.redo_button.connect('clicked', self._on_button_redo_clicked, buffer)
        self.hbox.pack_start(self.redo_button, False)

        # Annotation buttons.
        button = gtk.Button(label = "Add annotation")
        button.set_properties(can_focus = False)
        button.connect('clicked', self._on_button_add_annotation_clicked)
        self.hbox.pack_start(button)

        button = gtk.ToggleButton(label = "Show annotations")
        button.set_active(True)
        button.set_properties(can_focus = False)
        button.connect('toggled', self._on_button_show_annotations_toggled)
        self.hbox.pack_start(button)

        # Pack widgets.
        self.scroll.add(self.view)
        self.add(self.vbox)
        self.vbox.pack_start(self.hbox, False)
        self.vbox.pack_start(self.scroll)
        self.show_all()

        # Enable spell checking.
        lang = locale.getlocale()[0]
        if lang is None:
            print "WARNING: Spell check disabled because language is not set."
        else:
            gtkspell.Spell(self.view).set_language(lang)

        # Insert some text.
        buffer.insert_at_cursor('Test me please.')
        range = buffer.get_bounds()
        tag   = buffer.create_tag('link_to_debain_org',
                                  foreground = 'blue',
                                  underline  = pango.UNDERLINE_SINGLE)
        tag.set_data('link', 'http://debain.org')
        buffer.apply_tag(tag, *range)

        dump = buffer.dump()

        buffer.delete(*range)
        buffer.restore(dump)


    def _on_link_clicked(self, buffer, link):
        print 'Link clicked:', link


    def _on_buffer_undo_stack_changed(self, buffer):
        self.undo_button.set_sensitive(buffer.can_undo())
        self.redo_button.set_sensitive(buffer.can_redo())


    def _on_button_format_clicked(self, button, buffer, format):
        buffer.toggle_selection_tag(format)


    def _on_button_undo_clicked(self, button, buffer):
        buffer.undo()


    def _on_button_redo_clicked(self, button, buffer):
        buffer.redo()


    def _mk_annotation_name(self):
        self.n_annotations += 1
        return 'annotation%d' % self.n_annotations


    def _on_annotation_focus_out_event(self, editor, annotation):
        if annotation.get_text() == '':
            editor.get_buffer().remove_annotation(annotation)


    def _add_annotation(self, mark):
        annotation = Annotation(mark)
        annotation.set_bg_color(gtk.gdk.color_parse('lightblue'))
        annotation.set_border_color(gtk.gdk.color_parse('blue'))
        annotation.set_title('Annotation')
        annotation.set_text('Annotation number %d.' % self.n_annotations)
        self.view.get_buffer().add_annotation(annotation)
        return annotation


    def _on_button_add_annotation_clicked(self, button):
        buffer     = self.view.get_buffer()
        cursor_pos = buffer.get_property('cursor-position')
        iter       = buffer.get_iter_at_offset(cursor_pos)
        mark       = buffer.create_mark(self._mk_annotation_name(),
                                        iter,
                                        iter.is_end())
        self._add_annotation(mark)


    def _on_button_show_annotations_toggled(self, button):
        active = button.get_active()
        self.view.set_show_annotations(active)


# Create widgets.
window = Window()
window.connect('delete-event', gtk.main_quit)
gtk.main()
