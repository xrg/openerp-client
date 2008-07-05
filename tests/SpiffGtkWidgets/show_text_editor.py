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
        self.view.modify_font(pango.FontDescription("Arial 12"))
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.set_size_request(600, 600)
        self.vbox.set_border_width(6)
        self.vbox.set_spacing(6)
        self.hbox.set_spacing(6)

        button = gtk.Button(stock = gtk.STOCK_BOLD)
        button.set_properties(can_focus = False)
        button.connect('clicked', self._on_button_bold_clicked, buffer)
        self.hbox.pack_start(button, False)

        button = gtk.Button(stock = gtk.STOCK_UNDO)
        button.set_properties(can_focus = False)
        button.connect('clicked', self._on_button_undo_clicked, buffer)
        self.hbox.pack_start(button, False)

        button = gtk.Button(stock = gtk.STOCK_REDO)
        button.set_properties(can_focus = False)
        button.connect('clicked', self._on_button_redo_clicked, buffer)
        self.hbox.pack_start(button, False)

        # Pack widgets.
        self.scroll.add_with_viewport(self.view)
        self.add(self.vbox)
        self.vbox.pack_start(self.hbox, False)
        self.vbox.pack_start(self.scroll)
        self.show_all()

        self.bold = buffer.create_tag('bold', weight = pango.WEIGHT_BOLD)


    def _on_button_bold_clicked(self, button, buffer):
        bounds = buffer.get_selection_bounds()
        if not bounds:
            return
        buffer.apply_tag(self.bold, *bounds)


    def _on_button_undo_clicked(self, button, buffer):
        buffer.undo()


    def _on_button_redo_clicked(self, button, buffer):
        buffer.redo()


# Create widgets.
window = Window()
window.connect('delete-event', gtk.main_quit)
gtk.main()
