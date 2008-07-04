import sys, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
import gtk
from SpiffGtkWidgets.AnnotatedTextView import AnnotatedTextView, Annotation

class Window(gtk.Window):
    n_annotations = 0

    def __init__(self):
        gtk.Window.__init__(self)
        self.vbox   = gtk.VBox()
        self.hbox   = gtk.HBox()
        self.scroll = gtk.ScrolledWindow()
        self.buffer = gtk.TextBuffer()
        self.view   = AnnotatedTextView(self.buffer)
        self.view.connect('button-press-event', self._on_view_button_press_event)
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.set_size_request(600, 600)
        self.vbox.set_border_width(6)
        self.vbox.set_spacing(6)
        self.hbox.set_spacing(6)

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
        self.scroll.add_with_viewport(self.view)
        self.add(self.vbox)
        self.vbox.pack_start(self.hbox, False)
        self.vbox.pack_start(self.scroll)
        self.show_all()

        iter = self.buffer.get_start_iter()
        for i in range(400):
            self.buffer.insert(iter, 'Click anywhere in the text\n')

        # Add an annotation that points to the beginning of the document.
        iter = self.buffer.get_start_iter()
        mark = self.buffer.create_mark('start', iter)
        self._add_annotation(mark)

        # Add an annotation that points to the beginning of the document.
        iter = self.buffer.get_iter_at_line_offset(2, 0)
        mark = self.buffer.create_mark('second_line', iter)
        self._add_annotation(mark)


    def _mk_annotation_name(self):
        self.n_annotations += 1
        return 'annotation%d' % self.n_annotations


    def _on_annotation_buffer_changed(self, buffer, annotation):
        if buffer.get_text(*buffer.get_bounds()) == '':
            self.view.remove_annotation(annotation)


    def _add_annotation(self, mark):
        annotation = Annotation(mark)
        annotation.modify_bg(gtk.gdk.color_parse('lightblue'))
        annotation.modify_border(gtk.gdk.color_parse('blue'))
        annotation.set_title('Annotation')
        annotation.set_text('Annotation number %d.' % self.n_annotations)
        annotation.show_all()
        self.view.add_annotation(annotation)
        annotation.buffer.connect('changed', self._on_annotation_buffer_changed, annotation)
        return annotation


    def _on_view_button_press_event(self, view, event):
        iter = view.get_iter_at_location(int(event.x), int(event.y))


    def _on_button_add_annotation_clicked(self, button):
        cursor_pos = self.buffer.get_property('cursor-position')
        start      = self.buffer.get_iter_at_offset(cursor_pos)
        mark       = self.buffer.create_mark(self._mk_annotation_name(), start)
        self._add_annotation(mark)


    def _on_button_show_annotations_toggled(self, button):
        active = button.get_active()
        self.view.set_show_annotations(active)


# Create widgets.
window = Window()
window.connect('delete-event', gtk.main_quit)
gtk.main()
