import locale, gettext
gettext.install('test')
import pygtk
pygtk.require('2.0')
import gtk

import rpc
rpc.session.login('admin', 'admin', 'localhost', 8069)

from screen.screen import Screen
sc = Screen('res.country')

def switch(button, *args):
	button.current_id = (button.current_id + 1) % 4
	sc.display(button.current_id)

window = gtk.Window()
table = gtk.Table(2, 1)
window.add(table)
table.attach(sc.current_view.widget, 0, 1, 0, 1)
button = gtk.Button('next')
button.connect('clicked', switch)
table.attach(button, 0, 1, 1, 2)
window.show_all()
sc.load([11,22,33,44])
sc.display(0)
print sc.widget
button.current_id = 0
gtk.main()
