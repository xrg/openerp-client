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
import tools
import gtk
import gtk.glade
import gettext
import common
from datetime import datetime

from SpiffGtkWidgets import Calendar
from mx import DateTime


class ViewCalendar(object):
    def __init__(self, model, axis, fields, attrs):
        self.glade = gtk.glade.XML(common.terp_path("terp.glade"),'widget_view_calendar',gettext.textdomain())
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
        sc.select_day(t[2])

        if models:
            # If doesn't work, remove events
            self.cal_model = Calendar.Model()
            self.cal_view.model = self.cal_model

            for model in models.models:
                event = Calendar.Event(
                    'Event number 1',
                    datetime(2008, 9, 8, 02),
                    datetime(2008, 9, 8, 17),
                    bg_color = 'lightgreen')
                self.cal_model.add_event(event)

class parser_calendar(interface.parser_interface):
    def parse(self, model, root_node, fields):
        attrs = tools.node_attributes(root_node)
        self.title = attrs.get('string', 'Calendar')

        axis = []
        axis_data = {}
        for node in root_node.childNodes:
            node_attrs = tools.node_attributes(node)
            if node.localName == 'field':
                axis.append(str(node_attrs['name']))
                axis_data[str(node_attrs['name'])] = node_attrs

        view = ViewCalendar(model, axis, fields, attrs)

        return view, {}, [], ''

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

