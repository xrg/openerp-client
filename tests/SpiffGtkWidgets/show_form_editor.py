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
import sys, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
import gtk
from SpiffGtkWidgets.FormEditor import Workspace, Elements
from SpiffGtkWidgets.color      import to_gdk

class Window(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.vbox   = gtk.VBox()
        self.hbox   = gtk.HBox()
        self.editor = Workspace()
        self.set_size_request(800, 600)
        self.vbox.set_border_width(6)
        self.vbox.set_spacing(6)
        self.hbox.set_spacing(6)
        #editor.connect('undo-stack-changed', self._on_undo_stack_changed)

        # Editor buttons.
        button = gtk.Button(stock = gtk.STOCK_CLEAR)
        button.set_properties(can_focus = False)
        button.connect('clicked', self._on_button_clear_clicked)
        self.hbox.pack_start(button, False)

        # Undo/redo buttons.
        self.undo_button = gtk.Button(stock = gtk.STOCK_UNDO)
        self.undo_button.set_properties(can_focus = False)
        #self.undo_button.set_sensitive(self.editor.can_undo())
        self.undo_button.connect('clicked', self._on_button_undo_clicked)
        self.hbox.pack_start(self.undo_button, False)

        self.redo_button = gtk.Button(stock = gtk.STOCK_REDO)
        self.redo_button.set_properties(can_focus = False)
        #self.redo_button.set_sensitive(self.editor.can_redo())
        self.redo_button.connect('clicked', self._on_button_redo_clicked)
        self.hbox.pack_start(self.redo_button, False)

        # Pack widgets.
        self.add(self.vbox)
        self.vbox.pack_start(self.hbox, False)
        self.vbox.pack_start(self.editor)
        self.show_all()


    def _on_undo_stack_changed(self, editor):
        self.undo_button.set_sensitive(editor.can_undo())
        self.redo_button.set_sensitive(editor.can_redo())


    def _on_button_clear_clicked(self, button):
        self.editor.clear()


    def _on_button_undo_clicked(self, button):
        self.editor.undo()


    def _on_button_redo_clicked(self, button):
        self.editor.redo()


# Create widgets.
window = Window()
window.connect('delete-event', gtk.main_quit)
gtk.main()
