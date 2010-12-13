import sys, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
import gtk
from SpiffGtkWidgets import Calendar
import datetime

def on_event_clicked(calendar, event, ev, model):
    print "Event %s was clicked" % event.caption
    model.remove_event(event)

def on_time_clicked(calendar, time, event):
    print "Time %s was clicked" % time

def on_date_clicked(calendar, date, event):
    print "Date %s was clicked" % date

def on_day_selected(calendar, day, event):
    print "Day %s was selected" % day

def on_day_activate(calendar, day, event):
    print "Day %s was activated" % day

window   = gtk.Window()
model    = Calendar.Model()
calendar = Calendar.Calendar(model)

# Normal events.
event = Calendar.Event('Event number 1',
                       datetime.datetime(2008, 6, 8, 02),
                       datetime.datetime(2008, 6, 8, 17),
                       bg_color = 'lightgreen')
model.add_event(event)
event = Calendar.Event('Event number 2',
                       datetime.datetime(2008, 6, 8, 12),
                       datetime.datetime(2008, 6, 8, 14),
                       bg_color = 'lightblue')
model.add_event(event)
event = Calendar.Event('Event number 3',
                       datetime.datetime(2008, 6, 8, 15),
                       datetime.datetime(2008, 6, 8, 16, 30),
                       bg_color = 'lightgrey')
model.add_event(event)
event = Calendar.Event('Event number 3b',
                       datetime.datetime(2008, 6, 8, 15, 30),
                       datetime.datetime(2008, 6, 8, 17, 15),
                       bg_color = 'lightgrey')
model.add_event(event)
event = Calendar.Event('Event number 4',
                       datetime.datetime(2008, 6, 8, 17),
                       datetime.datetime(2008, 6, 8, 18),
                       bg_color = 'yellow')
model.add_event(event)

# A normal multi-day event.
event = Calendar.Event('Long Event',
                       datetime.datetime(2008, 6, 9),
                       datetime.datetime(2008, 6, 11))
model.add_event(event)

# The following events are all-day events and displayed differently in
# week mode.
event = Calendar.Event('One-day Event', datetime.datetime(2008, 6, 9))
model.add_event(event)
event = Calendar.Event('Eight-day Event',
                       datetime.datetime(2008, 6, 8),
                       datetime.datetime(2008, 6, 15),
                       all_day    = True,
                       bg_color   = 'navy',
                       text_color = 'white')
model.add_event(event)

#calendar.select_from_tuple((2008, 10, 8))
#calendar.select_next_page()
#calendar.select_previous_page()
window.add(calendar)
window.set_size_request(600, 600)
window.show_all()

window.connect('delete-event', gtk.main_quit)
calendar.connect('event-clicked', on_event_clicked, model)
calendar.connect('date-clicked',  on_date_clicked)
calendar.connect('time-clicked',  on_time_clicked)
calendar.connect('day-selected',  on_day_selected)
calendar.connect('day-activate',  on_day_activate)
gtk.main()
