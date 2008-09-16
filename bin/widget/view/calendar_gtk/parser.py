# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from widget.view import interface
from tools import ustr, node_attributes 
import gtk
import gtk.glade
import gettext
import common
from datetime import datetime

from SpiffGtkWidgets import Calendar
from mx import DateTime
import time

from tools.debug import logged


COLOR_PALETTE = ['#f57900', '#cc0000', '#d400a8', '#75507b', '#3465a4', '#73d216', '#c17d11', '#edd400',
                 '#fcaf3e', '#ef2929', '#ff00c9', '#ad7fa8', '#729fcf', '#8ae234', '#e9b96e', '#fce94f',
                 '#ff8e00', '#ff0000', '#b0008c', '#9000ff', '#0078ff', '#00ff00', '#e6ff00', '#ffff00',
                 '#905000', '#9b0000', '#840067', '#510090', '#0000c9', '#009b00', '#9abe00', '#ffc900',]

_colorline = ['#%02x%02x%02x' % (25+((r+10)%11)*23,5+((g+1)%11)*20,25+((b+4)%11)*23) for r in range(11) for g in range(11) for b in range(11) ]
def choice_colors(n):
    if n > len(COLOR_PALETTE):
        return _colorline[0:-1:len(_colorline)/(n+1)]
    elif n:
        return COLOR_PALETTE[:n]
    return []

class TinyEvent(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        r = []
        for x in self.__dict__:
            r.append("%s: %r" % (x, self.__dict__[x]))
        return "\n".join(r)


class ViewCalendar(object):
    #@logged(False)
    def __init__(self, model, axis, fields, attrs):
        self.glade = gtk.glade.XML(common.terp_path("openerp.glade"),'widget_view_calendar',gettext.textdomain())
        self.widget = self.glade.get_widget('widget_view_calendar')

        self.fields = fields
        self.attrs = attrs
        self.axis = axis

        self.cal_model = Calendar.Model()
        self.cal_view = Calendar.Calendar(self.cal_model)
        vbox = self.glade.get_widget('cal_vbox')
        vbox.pack_start(self.cal_view)
        vbox.show_all()

        self.process = False
        self.glade.signal_connect('on_but_forward_clicked', self._back_forward, 1)
        self.glade.signal_connect('on_but_back_clicked', self._back_forward, -1)
        self.glade.signal_connect('on_but_today_clicked', self._today, -1)
        self.glade.signal_connect('on_calendar_small_day_selected_double_click', self._change_small)
        self.glade.signal_connect('on_button_day_clicked', self._change_view, 'day')
        self.glade.signal_connect('on_button_week_clicked', self._change_view, 'week')
        self.glade.signal_connect('on_button_month_clicked', self._change_view, 'month')
        self.date = DateTime.now()
        self.mode = 'month'

        self.string = attrs.get('string', '')
        self.date_start = attrs.get('date_start') 
        self.date_delay = attrs.get('date_delay')
        self.date_stop = attrs.get('date_stop')
        self.color_field = attrs.get('color')
        self.day_length = int(attrs.get('day_length', 8))
        self.colors = {}
        self.models = None
    

    def _change_small(self, widget, *args, **argv):
        t = list(widget.get_date() )
        t[1] += 1
        self.date = DateTime.DateTime(*t)
        self.display(None)

    def _today(self, widget, type, *args, **argv):
        self.date = DateTime.now()
        self.display(None)

    def _back_forward(self, widget, type, *args, **argv):
        if self.mode=='day':
            self.date = self.date + DateTime.RelativeDateTime(days=type)
        if self.mode=='week':
            self.date = self.date + DateTime.RelativeDateTime(weeks=type)
        if self.mode=='month':
            self.date = self.date + DateTime.RelativeDateTime(months=type)
        self.display(None)

    def _change_view(self, widget, type, *args, **argv):
        if self.process or self.mode == type:
            return True
        self.process = True
        self.mode = type
        self.display(None)
        self.process = False
        return True

    #@logged(False)
    def display(self, models):
        label = self.glade.get_widget('label_current')
        t = self.date.tuple()
        if self.mode=='month':
            self.glade.get_widget('radio_month').set_active(True)
            d1 = datetime(*list(t)[:6])
            self.cal_view.set_range(self.cal_view.RANGE_MONTH)
            self.cal_view.select(d1)
            label.set_text(self.date.strftime('%B %Y'))
        elif self.mode=='week':
            self.glade.get_widget('radio_week').set_active(True)
            self.cal_view.set_range(self.cal_view.RANGE_WEEK)
            d1 = datetime(*list(t)[:6])
            self.cal_view.select(d1)
            label.set_text(_('Week') + ' ' + self.date.strftime('%W, %Y'))
        elif self.mode=='day':
            self.glade.get_widget('radio_day').set_active(True)
            self.cal_view.set_range(self.cal_view.RANGE_CUSTOM)
            d1 = datetime(*(list(t)[:3] + [00]))
            d2 = datetime(*(list(t)[:3] + [23, 59, 59]))
            self.cal_view.set_custom_range(d1,d2)
            label.set_text(self.date.strftime('%A %x'))
        sc = self.glade.get_widget('calendar_small')
        sc.select_month(t[1]-1,t[0])
        day = t[2]
        sc.select_day(day)
         
        if models:
            self.models = models.models

        if self.models:
            if self.color_field:
                self.colors = {}
                for model in self.models:
                    evt = model.get()
                    key = evt[self.color_field]
                    name = key
                    value = key
                
                    if isinstance(key, (tuple, list)):
                        value, name = key

                    self.colors[key] = (name, value, None)

                colors = choice_colors(len(self.colors))
                for i, (key, value) in enumerate(self.colors.items()):
                    self.colors[key] = (value[0], value[1], colors[i])
   
           
            # If doesn't work, remove events
            self.cal_model = Calendar.Model()
            self.cal_view.model = self.cal_model


            for model in self.models:
                evt = model.get()
                self.__convert(evt)
                e = self.__get_event(evt)
            
                #print "event:", repr(e)
                #if not (e.dayspan > 0 and day - e.dayspan < e.starts) or (e.dayspan == 0 and day <= e.starts):
                #    continue
                #print " -> shown"

                #print e.starts
                event = Calendar.Event(
                    e.title,
                    datetime(*e.starts[:7]),
                    datetime(*e.ends[:7]),
                    bg_color = e.color)
                self.cal_model.add_event(event)


    def __convert(self, event):
        # method from eTiny
        DT_SERVER_FORMATS = {
          'datetime': '%Y-%m-%d %H:%M:%S',
          'date': '%Y-%m-%d',
          'time': '%H:%M:%S'
        }

        fields = [x for x in [self.date_start, self.date_stop] if x]
        for fld in fields:
            typ = self.fields[fld]['type']
            fmt = DT_SERVER_FORMATS[typ]

            if event[fld] and fmt:
                event[fld] = time.strptime(event[fld], fmt)
            
            # default start time is 9:00 AM
            if typ == 'date' and fld == self.date_start:
                ds = list(event[fld])
                ds[3] = 9
                event[fld] = tuple(ds)

    def __get_event(self, event):

        title = ''       # the title
        description = [] # the description
        starts = None    # the starting time (datetime)
        ends = None      # the end time (datetime)
        
        if self.axis:
            
            f = self.axis[0]
            s = event[f]
            
            if isinstance(s, (tuple, list)): s = s[-1]
            
            title = ustr(s)
        
            for f in self.axis[1:]:
                s = event[f]
                if isinstance(s, (tuple, list)): s = s[-1]
            
                description += [ustr(s)]

        starts = event.get(self.date_start)
        ends = event.get(self.date_delay) or 1.0
        span = 0
        
        if starts and ends:
            
            n = 0
            h = ends
            
            if ends == self.day_length: span = 1
            
            if ends > self.day_length:
                n = ends / self.day_length
                h = ends % self.day_length
            
                n = int(math.floor(n))
            
                if n > 0: span = n + 1
            
            ends = time.localtime(time.mktime(starts) + (h * 60 * 60) + (n * 24 * 60 * 60))
        
        if starts and self.date_stop:
            
            ends = event.get(self.date_stop)
            if not ends:
                ends = time.localtime(time.mktime(starts) + 60 * 60)
                
            tds = time.mktime(starts)
            tde = time.mktime(ends)
            
            if tds >= tde:
                tde = tds + 60 * 60
                ends = time.localtime(tde)
            
            n = (tde - tds) / (60 * 60)
            
            if n > self.day_length:
                span = math.floor(n / 24)

        #starts = format.format_datetime(starts, "datetime", True)
        #ends = format.format_datetime(ends, "datetime", True)
        
        color_key = event.get(self.color_field) 
        color = self.colors.get(color_key)

        title = title.strip()
        description = ', '.join(description).strip()
        
        return TinyEvent(event=event, starts=starts, ends=ends, title=title, description=description, dayspan=span, color=(color or None) and color[-1])



class parser_calendar(interface.parser_interface):
    def parse(self, model, root_node, fields):
        attrs = node_attributes(root_node)
        self.title = attrs.get('string', 'Calendar')

        axis = []
        axis_data = {}
        for node in root_node.childNodes:
            node_attrs = node_attributes(node)
            if node.localName == 'field':
                axis.append(str(node_attrs['name']))
                axis_data[str(node_attrs['name'])] = node_attrs

        view = ViewCalendar(model, axis, fields, attrs)

        return view, {}, [], ''

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

