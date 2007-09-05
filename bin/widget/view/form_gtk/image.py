##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import os
from base64 import encodestring, decodestring

import pygtk
pygtk.require('2.0')
import gtk

import common
import interface
import tempfile
import urllib

NOIMAGE = file(common.terp_path_pixmaps("noimage.png"), 'rb').read()


class image_wid(interface.widget_interface):

	def __init__(self, window, parent, model, attrs={}):
		interface.widget_interface.__init__(self, window, parent=parent, attrs=attrs)

		self._value = ''
		self.height = int(attrs.get('img_height', 100))
		self.width = int(attrs.get('img_width', 300))

		self.widget = gtk.HBox(spacing=5)
		self.event = gtk.EventBox()
		self.event.drag_dest_set(gtk.DEST_DEFAULT_ALL, [
			('text/plain', 0, 0),
			('text/uri-list', 0, 1),
			("image/x-xpixmap", 0, 2)], gtk.gdk.ACTION_MOVE)
		self.event.connect('drag_motion', self.drag_motion)
		self.event.connect('drag_data_received', self.drag_data_received)

		self.image = gtk.Image()
		self.event.add(self.image)
		self.widget.pack_start(self.event, expand=True, fill=True)

		self.vbox = gtk.VBox()
		self.hbox = gtk.HBox(spacing=5)
		self.but_add = gtk.Button(stock='gtk-open')
		self.but_add.connect('clicked', self.sig_add)
		self.hbox.pack_start(self.but_add, expand=False, fill=False)

		self.but_save_as = gtk.Button(stock='gtk-save-as')
		self.but_save_as.connect('clicked', self.sig_save_as)
		self.hbox.pack_start(self.but_save_as, expand=False, fill=False)

		self.but_remove = gtk.Button(stock='gtk-clear')
		self.but_remove.connect('clicked', self.sig_remove)
		self.hbox.pack_start(self.but_remove, expand=False, fill=False)

		self.vbox.pack_start(self.hbox, expand=True, fill=False)
		self.widget.pack_start(self.vbox, expand=False, fill=False)

		self.update_img()

	def sig_add(self, widget):
		filter_all = gtk.FileFilter()
		filter_all.set_name(_('All files'))
		filter_all.add_pattern("*")

		filter_image = gtk.FileFilter()
		filter_image.set_name(_('Images'))
		for mime in ("image/png", "image/jpeg", "image/gif"):
			filter_image.add_mime_type(mime)
		for pat in ("*.png", "*.jpg", "*.gif", "*.tif", "*.xpm"):
			filter_image.add_pattern(pat)

		filename = common.file_selection(_('Open...'), parent=self._window, preview=True,
				filters=[filter_image, filter_all])
		if filename:
			self._value = encodestring(file(filename, 'rb').read())
			self.update_img()

	def sig_save_as(self, widget):
		filename = common.file_selection(_('Save As...'), parent=self._window,
				action=gtk.FILE_CHOOSER_ACTION_SAVE)
		if filename:
			file(filename, 'wb').write(decodestring(self._value))
	
	def sig_remove(self, widget):
		self._value = ''
		self.update_img()

	def drag_motion(self, widget, context, x, y, timestamp):
		context.drag_status(gtk.gdk.ACTION_COPY, timestamp)
		return True

	def drag_data_received(self, widget, context, x, y, selection,
			info, timestamp):
		if info == 0:
			uri = selection.get_text().split('\n')[0]
			if uri:
				self._value = encodestring(urllib.urlopen(uri).read())
			self.update_img()
		elif info == 1:
			uri = selection.data.split('\r\n')[0]
			if uri:
				self._value = encodestring(urllib.urlopen(uri).read())
			self.update_img()
		elif info == 2:
			data = selection.get_pixbuf()
			if data:
				self._value = encodestring(data)
				self.update_img()

	def update_img(self):
		if not self._value:
			data = NOIMAGE
		else:
			data = decodestring(self._value)

		pixbuf = None
		for type in ('jpeg', 'gif', 'png', 'bmp'):
			loader = gtk.gdk.PixbufLoader(type)
			try:
				loader.write(data, len(data))
			except:
				continue
			pixbuf = loader.get_pixbuf()
			if pixbuf:
				break
		if not pixbuf:
			loader = gtk.gdk.PixbufLoader('png')
			loader.write(NOIMAGE, len(NOIMAGE))
			pixbuf = loader.get_pixbuf()

		loader.close()

		img_height = pixbuf.get_height()
		if img_height > self.height:
			height = self.height
		else:
			height = img_height

		img_width = pixbuf.get_width()
		if img_width > self.width:
			width = self.width
		else:
			width = img_width

		if (img_width / width) < (img_height / height):
			width = float(img_width) / float(img_height) * float(height)
		else:
			height = float(img_height) / float(img_width) * float(width)

		scaled = pixbuf.scale_simple(int(width), int(height), gtk.gdk.INTERP_BILINEAR)
		self.image.set_from_pixbuf(scaled)

	def display(self, model, model_field):
		if not model_field:
			return False
		self._value = model_field.get(model)
		super(image_wid, self).display(model, model_field)
		self.update_img()

	def set_value(self, model, model_field):
		return model_field.set_client(model, self._value or False)
