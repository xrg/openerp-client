import sys, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
import gtk
from SpiffGtkWidgets import AnnotatedTextView, Annotation

class Window(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.scroll = gtk.ScrolledWindow()
        self.buffer = gtk.TextBuffer()
        self.view   = AnnotatedTextView(self.buffer)
        self.view.connect('button-press-event', self._on_view_button_press_event)
        self.buffer.connect('mark-set', self._on_buffer_mark_set)

        self.scroll.add_with_viewport(self.view)
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(self.scroll)
        self.set_size_request(600, 600)
        self.show_all()

        iter = self.buffer.get_start_iter()
        for i in range(400):
            self.buffer.insert(iter, 'Click anywhere in the text\n')

        # Add an annotation that points to the beginning of the document.
        iter       = self.buffer.get_start_iter()
        mark       = self.buffer.create_mark('start', iter)
        annotation = Annotation(mark)
        annotation.modify_bg(gtk.gdk.color_parse('lightblue'))
        annotation.modify_border(gtk.gdk.color_parse('blue'))
        annotation.set_title('Comment')
        annotation.set_text('The very first character is here.')
        annotation.show_all()
        self.view.add_annotation(annotation)

        # Add an annotation that points to the beginning of the document.
        iter       = self.buffer.get_iter_at_line_offset(2, 0)
        mark       = self.buffer.create_mark('second_line', iter)
        annotation = Annotation(mark)
        annotation.modify_bg(gtk.gdk.color_parse('lightblue'))
        annotation.modify_border(gtk.gdk.color_parse('blue'))
        annotation.set_title('Comment')
        annotation.set_text('Second line is here.')
        annotation.show_all()
        self.view.add_annotation(annotation)


    def _on_buffer_mark_set(self, buffer, iter, mark):
        rect = self.view.get_iter_location(iter)
    

    def _on_view_button_press_event(self, view, event):
        # Add an annotation that points to the click location.
        iter       = view.get_iter_at_location(int(event.x), int(event.y))
        mark       = self.buffer.create_mark('whatever %d' % event.y, iter)
        annotation = Annotation(mark)
        annotation.modify_bg(gtk.gdk.color_parse('lightblue'))
        annotation.modify_border(gtk.gdk.color_parse('blue'))
        annotation.set_title('Clicked')
        annotation.set_text('Annotation for %d, %d.' % (event.x, event.y))
        annotation.show_all()
        self.view.add_annotation(annotation)


# Create widgets.
window = Window()
window.connect('delete-event', gtk.main_quit)
gtk.main()
