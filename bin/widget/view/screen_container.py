##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import gtk
from gtk import glade

class screen_container(object):
	def __init__(self):
		self.old_widget = False
		self.sw = gtk.ScrolledWindow()
		self.sw.set_shadow_type(gtk.SHADOW_NONE)
		self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.vp = gtk.Viewport()
		self.vp.set_shadow_type(gtk.SHADOW_NONE)
		self.vbox = gtk.VBox()
		self.vbox.pack_end(self.sw)
		self.filter_vbox = None
		self.button = None

	def widget_get(self):
		return self.vbox

	def add_filter(self, widget, fnct, clear_fnct):
		self.filter_vbox = gtk.VBox(spacing=1)
		self.filter_vbox.set_border_width(1)
		label = gtk.Label(_('Search'))
		label.set_alignment(0.0, 0.5)
		label.show()
		self.filter_vbox.pack_start(label, expand=True, fill=False)
		hs = gtk.HSeparator()
		hs.show()
		self.filter_vbox.pack_start(hs, expand=True, fill=False)
		self.filter_vbox.pack_start(widget, expand=True, fill=True)
		hb = gtk.HButtonBox()
		hb.set_spacing(5)
		hb.set_layout(gtk.BUTTONBOX_END)
		button_clear = gtk.Button(stock=gtk.STOCK_CLEAR)
		button_clear.connect('clicked', clear_fnct)
		hb.pack_start(button_clear, expand=False, fill=False)
		self.button = gtk.Button(stock=gtk.STOCK_FIND)
		self.button.connect('clicked', fnct)
		self.button.set_property('can_default', True)
		hb.pack_start(self.button, expand=False, fill=False)
		hb.show_all()
		self.filter_vbox.pack_start(hb, expand=False, fill=False)
		hs = gtk.HSeparator()
		hs.show()
		self.filter_vbox.pack_start(hs, expand=True, fill=False)
		self.vbox.pack_start(self.filter_vbox, expand=False, fill=True)

	def show_filter(self):
		if self.filter_vbox:
			self.filter_vbox.show()
			# TODO find a way to put button has default action
			#self.button.set_property('has_default', True)

	def hide_filter(self):
		if self.filter_vbox:
			self.filter_vbox.hide()

	def set(self, widget):
		if self.vp.get_child():
			self.vp.remove(self.vp.get_child())
		if self.sw.get_child():
			self.sw.remove(self.sw.get_child())
		if not isinstance(widget, gtk.TreeView):
			self.vp.add(widget)
			widget = self.vp
		self.sw.add(widget)
		self.sw.show_all()

	def size_get(self):
		return self.sw.get_child().size_request()

