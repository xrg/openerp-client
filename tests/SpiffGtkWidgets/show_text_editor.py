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
import gtk
from SpiffGtkWidgets.TextEditor import TextEditor

class Window(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.vbox   = gtk.VBox()
        self.hbox   = gtk.HBox()
        self.scroll = gtk.ScrolledWindow()
        self.view   = TextEditor()
        buffer      = self.view.get_buffer()
        self.bold   = buffer.create_tag('bold',   weight = pango.WEIGHT_BOLD)
        self.italic = buffer.create_tag('italic', style  = pango.STYLE_ITALIC)
        self.uline  = buffer.create_tag('underline',
                                        underline = pango.UNDERLINE_SINGLE)
        self.view.modify_font(pango.FontDescription("Arial 12"))
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.set_size_request(600, 600)
        self.vbox.set_border_width(6)
        self.vbox.set_spacing(6)
        self.hbox.set_spacing(6)
        buffer.connect('undo-stack-changed',
                       self._on_buffer_undo_stack_changed)

        button = gtk.Button(stock = gtk.STOCK_BOLD)
        button.set_properties(can_focus = False)
        button.connect('clicked',
                       self._on_button_format_clicked,
                       buffer,
                       self.bold)
        self.hbox.pack_start(button, False)

        button = gtk.Button(stock = gtk.STOCK_ITALIC)
        button.set_properties(can_focus = False)
        button.connect('clicked',
                       self._on_button_format_clicked,
                       buffer,
                       self.italic)
        self.hbox.pack_start(button, False)

        button = gtk.Button(stock = gtk.STOCK_UNDERLINE)
        button.set_properties(can_focus = False)
        button.connect('clicked',
                       self._on_button_format_clicked,
                       buffer,
                       self.uline)
        self.hbox.pack_start(button, False)

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

        # Pack widgets.
        self.scroll.add_with_viewport(self.view)
        self.add(self.vbox)
        self.vbox.pack_start(self.hbox, False)
        self.vbox.pack_start(self.scroll)
        self.show_all()


    def _on_buffer_undo_stack_changed(self, buffer):
        self.undo_button.set_sensitive(buffer.can_undo())
        self.redo_button.set_sensitive(buffer.can_redo())


    def _on_button_format_clicked(self, button, buffer, format):
        bounds = buffer.get_selection_bounds()
        if not bounds:
            return
        buffer.apply_tag(format, *bounds)


    def _on_button_undo_clicked(self, button, buffer):
        buffer.undo()


    def _on_button_redo_clicked(self, button, buffer):
        buffer.redo()


# Create widgets.
window = Window()
window.connect('delete-event', gtk.main_quit)
gtk.main()
