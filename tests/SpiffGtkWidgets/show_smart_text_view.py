# -*- coding: UTF-8 -*-
import sys, os.path, pango
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
import gtk
from SpiffGtkWidgets.SmartTextView import SmartTextView, Annotation

class Window(gtk.Window):
    n_annotations = 0

    def __init__(self):
        gtk.Window.__init__(self)
        self.vbox   = gtk.VBox()
        self.hbox   = gtk.HBox()
        self.scroll = gtk.ScrolledWindow()
        self.buffer = gtk.TextBuffer()
        self.view   = SmartTextView(self.buffer)
        self.view.modify_font(pango.FontDescription("Arial 12"))
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.set_size_request(600, 600)
        self.vbox.set_border_width(6)
        self.vbox.set_spacing(6)
        self.hbox.set_spacing(6)

        button = gtk.Button(label = "Add annotation")
        button.connect('clicked', self._on_button_add_annotation_clicked)
        self.hbox.pack_start(button)
        button = gtk.Button(label = "Bold")
        button.connect('clicked', self._on_button_bold_clicked)
        self.hbox.pack_start(button)
        button = gtk.ToggleButton(label = "Show annotations")
        button.set_active(True)
        button.connect('toggled', self._on_button_show_annotations_toggled)
        self.hbox.pack_start(button)

        # Pack widgets.
        self.scroll.add_with_viewport(self.view)
        self.add(self.vbox)
        self.vbox.pack_start(self.hbox, False)
        self.vbox.pack_start(self.scroll)

        self.show_all()

        self.bold = self.buffer.create_tag('bold', weight = pango.WEIGHT_BOLD)


    def _mk_annotation_name(self):
        self.n_annotations += 1
        return 'annotation%d' % self.n_annotations


    def _on_button_add_annotation_clicked(self, button):
        cursor_pos = self.buffer.get_property('cursor-position')
        start      = self.buffer.get_iter_at_offset(cursor_pos)
        mark       = self.buffer.create_mark(self._mk_annotation_name(), start)
        annotation = Annotation(mark)
        annotation.modify_bg(gtk.gdk.color_parse('lightblue'))
        annotation.modify_border(gtk.gdk.color_parse('blue'))
        annotation.set_title('Comment')
        annotation.show_all()
        self.view.add_annotation(annotation)


    def _on_button_bold_clicked(self, button):
        bounds = self.buffer.get_selection_bounds()
        if not bounds:
            return
        self.buffer.apply_tag(self.bold, *bounds)


    def _on_button_show_annotations_toggled(self, button):
        active = button.get_active()
        self.view.set_show_annotations(active)


# Create widgets.
window = Window()
window.connect('delete-event', gtk.main_quit)
gtk.main()
