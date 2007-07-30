##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import os
from base64 import encodestring, decodestring

import pygtk
pygtk.require('2.0')
import gtk

import common
import interface


class image_wid(interface.widget_interface):

	def __init__(self, window, parent, model, attrs={}):
		interface.widget_interface.__init__(self, window, parent=parent, attrs=attrs)

		self._value = ''
		self.widget = gtk.EventBox()
		self.widget.connect("button_press_event", self.load_file)
		self.widget.connect("button_press_event", self.save_file)

		box1 = self.create_image(common.terp_path_pixmaps("noimage.png"))
		self.widget.add(box1)
		self.widget.show_all()

	def save_file(self, widget, event):
		if event.button != 3 or not self._value:
			return False
		chooser = gtk.FileChooserDialog(title=_('Save As...'), 
				action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(
					gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
					gtk.STOCK_SAVE, gtk.RESPONSE_OK), parent=self._window)
		res = chooser.run()
		if res == gtk.RESPONSE_OK:
			filename = chooser.get_filename()
			file(filename, 'wb').write(decodestring(self._value))
		chooser.destroy()

	def load_file(self, widget, event):
		if event.button != 1:
			return False
		chooser = gtk.FileChooserDialog(title=_('Open...'), 
				action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(
					gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
					gtk.STOCK_OPEN, gtk.RESPONSE_OK), parent=self._window)
		res = chooser.run()
		if res == gtk.RESPONSE_OK:
			filename = chooser.get_filename()
			self.update_img(filename)
			self._value = encodestring(file(filename, 'rb').read())
		chooser.destroy()

	def update_img(self, path):
		new_box = self.create_image(path)
		self.widget.remove(self.widget.get_child())
		self.widget.add(new_box)
		new_box.show()

	def display(self, model, model_field):
		if not model_field:
			return False
		self._value = model_field.get(model)
		super(image_wid, self).display(model, model_field)
		if self._value:
			try:
				fname = file(os.tempnam(), 'wb')
				fname.write(decodestring(self._value))
				fname.flush()
				self.update_img(fname.name)
			except:
				self.update_img(common.terp_path_pixmaps('noimage.png'))
		else:
			self.update_img(common.terp_path_pixmaps('noimage.png'))

	def set_value(self, model, model_field):
		return model_field.set_client(model, self._value or False)

	def create_image(self, img_filename):
		box1 = gtk.VBox(True)
		box1.set_border_width(2)

		# Now on to the image stuff
		self.image = gtk.Image()
		pixbuf = gtk.gdk.pixbuf_new_from_file(img_filename)
		width_widget = max(self.widget.allocation.width, 70) - 16
		pix_width, pix_height = pixbuf.get_width(), pixbuf.get_height()
		height = int(pix_height / (pix_width / float(width_widget)))
		if height > 100:
			height = 100
			width_widget = int(pix_width / (pix_height / 100.0))
		scaled = pixbuf.scale_simple(width_widget, height, gtk.gdk.INTERP_BILINEAR)
		self.image.set_from_pixbuf(scaled)

		box1.pack_start(self.image, True, True, 3)
		self.image.show()
		return box1
