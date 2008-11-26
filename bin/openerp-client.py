#!/usr/bin/python
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

"""
OpenERP - Client
OpenERP is an ERP+CRM program for small and medium businesses.

The whole source code is distributed under the terms of the
GNU Public Licence.

(c) 2003-TODAY, Fabien Pinckaers - Tiny sprl
"""
import sys, os
import release
__author__ = release.author
__version__ = release.version

import __builtin__
__builtin__.__dict__['openerp_version'] = __version__

import logging
logging.basicConfig()

from distutils.sysconfig import get_python_lib
terp_path = os.path.join(get_python_lib(), 'openerp-client')
sys.path.append(terp_path)

if os.name == 'nt':
    sys.path.insert(0, os.path.join(os.getcwd(), os.path.dirname(sys.argv[0]), 'GTK\\bin'))
    sys.path.insert(0, os.path.join(os.getcwd(), os.path.dirname(sys.argv[0]), 'GTK\\lib'))
    os.environ['PATH'] = os.path.join(os.getcwd(), os.path.dirname(sys.argv[0]), 'GTK\\lib') + ";" + os.environ['PATH']
    os.environ['PATH'] = os.path.join(os.getcwd(), os.path.dirname(sys.argv[0]), 'GTK\\bin') + ";" + os.environ['PATH']

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

import locale, gettext

import atk
import gtk._gtk
import pango

if os.name == 'nt':
    sys.path.insert(0, os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])))
    os.environ['PATH'] = os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])) + ";" + os.environ['PATH']

import translate
translate.setlang()

import options

# On first run, client won't have a language option,
# so try with the LANG environ, or fallback to english
client_lang = options.options['client.lang']
if client_lang is False:
    client_lang = os.environ.get('LANG', '')

translate.setlang(client_lang)

for logger in options.options['logging.logger'].split(','):
    if len(logger):
        loglevel = {'DEBUG':logging.DEBUG, 'INFO':logging.INFO, 'WARNING':logging.WARNING, 'ERROR':logging.ERROR, 'CRITICAL':logging.CRITICAL}
        log = logging.getLogger(logger)
        log.setLevel(loglevel[options.options['logging.level'].upper()])
if options.options['logging.verbose']:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.getLogger().setLevel(logging.ERROR)


import modules
import common

items = [('terp-flag', '_Translation', gtk.gdk.CONTROL_MASK, ord('t'), '')]
gtk.stock_add (items)

factory = gtk.IconFactory ()
factory.add_default ()

pix_file = os.path.join(os.getcwd(), os.path.dirname(sys.argv[0]), 'icons')
if not os.path.isdir(pix_file):
    pix_file = os.path.join(options.options['path.pixmaps'],'icons')

for fname in os.listdir(pix_file):
    ffname = os.path.join(pix_file,fname)
    if not os.path.isfile(ffname):
        continue
    iname = os.path.splitext(fname)[0]
    try:
        pixbuf = gtk.gdk.pixbuf_new_from_file(ffname)
    except:
        pixbuf = None
        continue
    if pixbuf:
        icon_set = gtk.IconSet (pixbuf)
        factory.add('terp-'+iname, icon_set)

try:
    win = modules.gui.main.terp_main()
    if not common.terp_survey():
        if options.options.rcexist:
            win.sig_login()
    gtk.main()
except KeyboardInterrupt, e:
    log = logging.getLogger('common')
    log.info(_('Closing OpenERP, KeyboardInterrupt'))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

