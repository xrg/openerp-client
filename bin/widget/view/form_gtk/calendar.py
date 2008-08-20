# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
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

import time
import datetime as DT
import gtk

import gettext

import common
import interface
import locale
import rpc
import service

import date_widget

DT_FORMAT = '%Y-%m-%d'
DHM_FORMAT = '%Y-%m-%d %H:%M:%S'
HM_FORMAT = '%H:%M:%S'

if not hasattr(locale, 'nl_langinfo'):
    locale.nl_langinfo = lambda *a: '%x'

if not hasattr(locale, 'D_FMT'):
    locale.D_FMT = None

class calendar(interface.widget_interface):
    def __init__(self, window, parent, model, attrs={}):
        interface.widget_interface.__init__(self, window, parent, attrs=attrs)
        self.format = locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y')
        self.widget = date_widget.ComplexEntry(self.format, spacing=3)
        self.entry = self.widget.widget
        self.entry.set_property('activates_default', True)
        self.entry.connect('button_press_event', self._menu_open)
        self.entry.connect('activate', self.sig_activate)
        self.entry.connect('focus-in-event', lambda x,y: self._focus_in())
        self.entry.connect('focus-out-event', lambda x,y: self._focus_out())

        tooltips = gtk.Tooltips()
        self.eb = gtk.EventBox()
        tooltips.set_tip(self.eb, _('Open the calendar widget'))
        tooltips.enable()
        self.eb.set_events(gtk.gdk.BUTTON_PRESS)
        self.eb.connect('button_press_event', self.cal_open, model, self._window)
        img = gtk.Image()
        img.set_from_stock('gtk-zoom-in', gtk.ICON_SIZE_MENU)
        img.set_alignment(0.5, 0.5)
        self.eb.add(img)
        self.widget.pack_start(self.eb, expand=False, fill=False)

        self.readonly=False

    def _color_widget(self):
        return self.entry

    def _readonly_set(self, value):
        interface.widget_interface._readonly_set(self, value)
        self.entry.set_editable(not value)
        self.entry.set_sensitive(not value)
        self.eb.set_sensitive(not value)

    def get_value(self, model):
        str = self.entry.get_text()
        if str=='':
            return False
        try:
            date = time.strptime(str, self.format)
        except:
            return False
        return time.strftime(DT_FORMAT, date)

    def set_value(self, model, model_field):
        model_field.set_client(model, self.get_value(model))
        return True

    def display(self, model, model_field):
        if not model_field:
            self.entry.clear()
            return False
        super(calendar, self).display(model, model_field)
        value = model_field.get(model)
        if not value:
            self.entry.clear()
        else:
            if len(value)>10:
                value=value[:10]
            date = time.strptime(value, DT_FORMAT)
            t=time.strftime(self.format, date)
            if len(t) > self.entry.get_width_chars():
                self.entry.set_width_chars(len(t))
            self.entry.set_text(t)
        return True

    def cal_open(self, widget, event, model=None, window=None):
        if self.readonly:
            common.message(_('This widget is readonly !'))
            return True

        if not window:
            window = service.LocalService('gui.main').window

        win = gtk.Dialog(_('Tiny ERP - Date selection'), window,
                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OK, gtk.RESPONSE_OK))
        win.set_icon(common.TINYERP_ICON)

        cal = gtk.Calendar()
        cal.display_options(gtk.CALENDAR_SHOW_HEADING|gtk.CALENDAR_SHOW_DAY_NAMES|gtk.CALENDAR_SHOW_WEEK_NUMBERS)
        cal.connect('day-selected-double-click', lambda *x: win.response(gtk.RESPONSE_OK))
        win.vbox.pack_start(cal, expand=True, fill=True)
        win.show_all()

        try:
            val = self.get_value(model)
            if val:
                cal.select_month(int(val[5:7])-1, int(val[0:4]))
                cal.select_day(int(val[8:10]))
        except ValueError:
            pass

        response = win.run()
        if response == gtk.RESPONSE_OK:
            year, month, day = cal.get_date()
            dt = DT.date(year, month+1, day)
            self.entry.set_text(dt.strftime(locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y')))
        self._focus_out()
        window.present()
        win.destroy()

class datetime(interface.widget_interface):
    def __init__(self, window, parent, model, attrs={}):
        interface.widget_interface.__init__(self, window, parent, model, attrs=attrs)
        self.format = locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y')+' %H:%M:%S'
        self.widget = date_widget.ComplexEntry(self.format, spacing=3)
        self.entry = self.widget.widget
        self.entry.set_property('activates_default', True)
        self.entry.connect('button_press_event', self._menu_open)
        self.entry.connect('focus-in-event', lambda x,y: self._focus_in())
        self.entry.connect('focus-out-event', lambda x,y: self._focus_out())

        tooltips = gtk.Tooltips()
        eb = gtk.EventBox()
        tooltips.set_tip(eb, _('Open the calendar widget'))
        tooltips.enable()
        eb.set_events(gtk.gdk.BUTTON_PRESS)
        eb.connect('button_press_event', self.cal_open, model, self._window)
        img = gtk.Image()
        img.set_from_stock('gtk-zoom-in', gtk.ICON_SIZE_MENU)
        img.set_alignment(0.5, 0.5)
        eb.add(img)
        self.widget.pack_start(eb, expand=False, fill=False)

        self.readonly=False

    def _color_widget(self):
        return self.entry

    def _readonly_set(self, value):
        self.readonly = value
        self.entry.set_editable(not value)
        self.entry.set_sensitive(not value)

    def get_value(self, model, timezone=True):
        str = self.entry.get_text()
        if str=='':
            return False
        try:
            date = time.strptime(str, self.format)
        except:
            return False
        if 'tz' in rpc.session.context and timezone:
            try:
                import pytz
                lzone = pytz.timezone(rpc.session.context['tz'])
                szone = pytz.timezone(rpc.session.timezone)
                dt = DT.datetime(date[0], date[1], date[2], date[3], date[4], date[5], date[6])
                ldt = lzone.localize(dt, is_dst=True)
                sdt = ldt.astimezone(szone)
                date = sdt.timetuple()
            except:
                pass
        return time.strftime(DHM_FORMAT, date)

    def set_value(self, model, model_field):
        model_field.set_client(model, self.get_value(model))
        return True

    def display(self, model, model_field):
        if not model_field:
            return self.show(False)
        super(datetime, self).display(model, model_field)
        self.show(model_field.get(model))
    
    def show(self, dt_val, timezone=True):
        if not dt_val:
            self.entry.clear()
        else:
            date = time.strptime(dt_val, DHM_FORMAT)
            if 'tz' in rpc.session.context and timezone:
                try:
                    import pytz
                    lzone = pytz.timezone(rpc.session.context['tz'])
                    szone = pytz.timezone(rpc.session.timezone)
                    dt = DT.datetime(date[0], date[1], date[2], date[3], date[4], date[5], date[6])
                    sdt = szone.localize(dt, is_dst=True)
                    ldt = sdt.astimezone(lzone)
                    date = ldt.timetuple()
                except:
                    pass
            t=time.strftime(self.format, date)
            if len(t) > self.entry.get_width_chars():
                self.entry.set_width_chars(len(t))
            self.entry.set_text(t)
        return True

    def cal_open(self, widget, event, model=None, window=None):
        if self.readonly:
            common.message(_('This widget is readonly !'))
            return True

        win = gtk.Dialog(_('Tiny ERP - Date selection'), window,
                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OK, gtk.RESPONSE_OK))

        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label(_('Hour:')), expand=False, fill=False)
        hour = gtk.SpinButton(gtk.Adjustment(0, 0, 23, 1, 5, 5), 1, 0)
        hbox.pack_start(hour, expand=True, fill=True)
        hbox.pack_start(gtk.Label(_('Minute:')), expand=False, fill=False)
        minute = gtk.SpinButton(gtk.Adjustment(0, 0, 59, 1, 10, 10), 1, 0)
        hbox.pack_start(minute, expand=True, fill=True)
        win.vbox.pack_start(hbox, expand=False, fill=True)

        cal = gtk.Calendar()
        cal.display_options(gtk.CALENDAR_SHOW_HEADING|gtk.CALENDAR_SHOW_DAY_NAMES|gtk.CALENDAR_SHOW_WEEK_NUMBERS)
        cal.connect('day-selected-double-click', lambda *x: win.response(gtk.RESPONSE_OK))
        win.vbox.pack_start(cal, expand=True, fill=True)
        win.show_all()

        try:
            val = self.get_value(model, timezone=False)
            if val:
                hour.set_value(int(val[11:13]))
                minute.set_value(int(val[-5:-3]))
                cal.select_month(int(val[5:7])-1, int(val[0:4]))
                cal.select_day(int(val[8:10]))
            else:
                hour.set_value(time.localtime()[3])
                minute.set_value(time.localtime()[4])
        except ValueError:
            pass
        response = win.run()
        if response == gtk.RESPONSE_OK:
            hr = int(hour.get_value())
            mi = int(minute.get_value())
            dt = cal.get_date()
            month = int(dt[1])+1
            day = int(dt[2])
            date = DT.datetime(dt[0], month, day, hr, mi)
            value = time.strftime(DHM_FORMAT, date.timetuple())
            self.show(value, timezone=False)
        self._focus_out()
        win.destroy()


class stime(interface.widget_interface):
    def __init__(self, window, parent, model, attrs={}):
        interface.widget_interface.__init__(self, parent, attrs=attrs)

        self.format = '%H:%M:%S'
        self.widget = date_widget.ComplexEntry(self.format, spacing=3)
        self.entry = self.widget.widget
        self.value=False

    def _readonly_set(self, value):
        self.readonly = value
        self.entry.set_editable(not value)
        self.entry.set_sensitive(not value)

    def _color_widget(self):
        return self.entry

    def get_value(self, model):
        str = self.entry.get_text()
        if str=='':
            res = False 
        try: 
            t = time.strptime(str, self.format)
        except:
            return False
        return time.strftime(HM_FORMAT, t)
        
    def set_value(self, model, model_field):
        res = self.get_value(model)
        model_field.set_client(model, res)
        return True

    def display(self, model, model_field):
        if not model_field:
            return self.show(False)
        super(stime, self).display(model, model_field)
        self.entry.set_text(model_field.get(model) or '00:00:00')
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

