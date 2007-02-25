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

# FileChooser is (c) 2004 Dave Kuhlman.
# under the MIT License Copyright 
class FileChooser(gtk.FileSelection):
	def __init__(self, title=_('Select a file'), modal=True, multiple=True):
		gtk.FileSelection.__init__(self, title=title)
		self.multiple = multiple
		self.connect("destroy", self.quit)
		self.connect("delete_event", self.quit)
		if modal:
			self.set_modal(True)
		self.cancel_button.connect('clicked', self.quit)
		self.ok_button.connect('clicked', self.ok_cb)
		if multiple:
			self.set_select_multiple(True)
##		 self.hide_fileop_buttons()
		self.ret = None
	def quit(self, *args):
		self.hide()
		self.destroy()
	def ok_cb(self, b):
		if self.multiple:
			self.ret = self.get_selections()
		else:
			self.ret = self.get_filename()
		self.quit()

class image_wid(interface.widget_interface):

	def __init__(self, window, parent, model, attrs={}):
		self._value = ''
		self.widget = gtk.Button()

		# Connect the "clicked" signal of the button to our callback
		self.widget.connect("clicked", self.load_file)
		self.widget.connect("button-press-event", self.save_file)

		# This calls our box creating function
		box1 = self.create_image("tinyerp_icon.png")

		# Pack and show all our widgets
		self.widget.add(box1)

		box1.show()
		self.widget.show()
		interface.widget_interface.__init__(self, window, parent=parent, attrs=attrs)

	def save_file(self, widget, event):
		if event.button != 3 or not self._value:
			return False
		filechooser = FileChooser(multiple=False, title=_('Save as ...'))
		filechooser.run()
		if filechooser.ret:
			file(filechooser.ret, 'w').write(decodestring(self._value))

	def load_file(self, widget):
		filechooser = FileChooser(multiple=False, title=_('Open file ...'))
		filechooser.run()
		if filechooser.ret:
			self.update_img(filechooser.ret)
			self._value = encodestring(file(filechooser.ret).read())
	
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
			fname = file(os.tempnam(), 'w')
			fname.write(decodestring(self._value))
			fname.flush()
			self.update_img(fname.name)
		else:
			self.update_img('tinyerp.png')

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
