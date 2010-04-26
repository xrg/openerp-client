# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import gtk
from gtk import glade
import gobject

import time
import locale

import rpc
import tools
from cStringIO import StringIO
from base64 import encodestring, decodestring

from common import terp_path_pixmaps
from widget.view import interface

class GalleryStore(gtk.ListStore):
    def __init__(self, model_group, *args):
        r = super(GalleryStore, self).__init__(*args)
        self.model_group = model_group
        return r

class ViewGallery(object):
    def __init__(self, model, fields, attrs, gallery_fields):
        self.widget = gtk.IconView()

        self.store = None
        self.field_text = gallery_fields['text']
        self.field_picture = gallery_fields['image']
        self.height = attrs.get('height', 75)
        self.width = attrs.get('width', 75)
        self.col = attrs.get('col', -1)

        # set some property of gtk.IconView
        self.widget.set_pixbuf_column(1)
        self.widget.set_text_column(2)
        self.widget.set_selection_mode(gtk.SELECTION_MULTIPLE)
        if self.col != -1 and self.col > 0:
            self.widget.set_columns(self.col)
        self.widget.set_item_width(self.width + 20)

        # Create a blank pictures
        self.blank_picture = gtk.gdk.pixbuf_new_from_file(terp_path_pixmaps('noimage.trans.png')).scale_simple(int(self.width), int(self.height), gtk.gdk.INTERP_BILINEAR)
        self.default_picture = self.create_composite_pixbuf(self.widget.render_icon('terp-eog-image-collection', gtk.ICON_SIZE_DIALOG))
        # Refresh

    def create_composite_pixbuf(self, pb):
        """Return composited pixbuf
        """
        # scale image if needed
        imgh = float(pb.get_height())
        h = float(imgh > self.height and self.height or imgh)
        imgw = float(pb.get_width())
        w = float(imgw > self.width and self.width or imgw)

        if (imgw / w) < (imgh / h):
            w = imgw / imgh * h
        else:
            h = imgh / imgw * w
        pb_scaled = pb.scale_simple(int(w), int(h), gtk.gdk.INTERP_BILINEAR)

        # create a composite image on top of blank pixbuf to make the picture
        # centered horizontally and verically
        pb_new = self.blank_picture.copy()
        pb_new_x = int((pb_new.get_width() - w) / 2.0)
        pb_new_y = int((pb_new.get_height() - h) / 2.0)

        pb_scaled.composite(pb_new,
                pb_new_x, pb_new_y,
                int(w), int(h),
                pb_new_x, pb_new_y,
                1.0, 1.0,
                gtk.gdk.INTERP_BILINEAR,
                255)

        return pb_new

    def create_store_model(self, mo):
        # try loading picture data
        pict_field = mo.mgroup.mfields.get(self.field_picture, False)
        pict_data = pict_field.get(mo)
        pict_buffer = None
        if pict_data:
            pict_data = decodestring(pict_data)
            pict_data_len = len(pict_data)
            for type in ('jpeg','gif','png','bmp','tiff'):
                loader = gtk.gdk.PixbufLoader(type)
                try:
                    loader.write(pict_data, pict_data_len)
                except:
                    continue
                pict_buffer = loader.get_pixbuf()
                if pict_buffer:
                    loader.close()
                    break

        # or use default picture (code from form_gtk/image.py)
        if not pict_buffer:
            pict_pixbuf = self.default_picture.copy()
        else:
            pict_pixbuf = self.create_composite_pixbuf(pict_buffer)

        return (mo, pict_pixbuf, mo.value[self.field_text])

    def create_store(self, model_group):
        return GalleryStore(model_group,
                            gobject.TYPE_PYOBJECT,
                            gtk.gdk.Pixbuf,
                            gobject.TYPE_STRING)

    def display(self, screen, reload=False):
        models = screen.models
        active_path = None
        active_screen_id = (screen.current_model and screen.current_model.id or None)

        if reload:
            # Create a store for our iconview and fill it with stock icons
            new_store = self.create_store(models)
            new_store.model_group = models

            for mo in (models and models.models or []):
                # add new line to store
                stor_item_data = self.create_store_model(mo)
                item_iter = new_store.append(stor_item_data)

            if self.store:
                self.widget.set_model(None)
                del(self.store)
            self.store = new_store
            self.widget.set_model(self.store)

        # update active item
        self.set_cursor(screen)

    def set_cursor(self, screen):
        current_model = screen.current_model
        if current_model:
            try:
                cursor = screen.models.models.index(current_model)
            except ValueError:
                # item was not found
                return
            self.select_path(cursor)
            self.widget.set_cursor(cursor)

    def select_path(self, path):
        self.widget.unselect_all()
        self.widget.select_path(path)
#        self.widget.scroll_to_path(path, False, 0.5, 0.5)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
