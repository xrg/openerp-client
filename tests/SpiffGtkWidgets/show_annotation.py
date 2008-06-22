import sys, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
import gtk
from SpiffGtkWidgets.AnnotatedTextView import Annotation

def on_button_press_event(annot, event):
    annot.set_text('Wow, that felt good.')

window     = gtk.Window()
annotation = Annotation(None)
annotation.modify_bg(gtk.gdk.color_parse('lightblue'))
annotation.modify_border(gtk.gdk.color_parse('blue'))
annotation.set_title('Samuel, 07-08-2008')

window.add(annotation)
window.set_size_request(200, 100)
window.show_all()

window.connect('delete-event', gtk.main_quit)
annotation.connect('button-press-event', on_button_press_event)
gtk.main()
