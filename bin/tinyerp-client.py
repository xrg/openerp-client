#!/usr/bin/python

##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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
"""
Tiny ERP - Client
Tiny ERP is an ERP+CRM program for small and medium businesses.

The whole source code is distributed under the terms of the
GNU Public Licence.

(c) 2003-TODAY, Fabien Pinckaers - Tiny sprl
"""
__author__ = 'Fabien Pinckaers, <fp@tiny.be>'
__version__ = "4.1.0"

import __builtin__
__builtin__.__dict__['tinyerp_version'] = __version__

import sys, os
import logging
logging.basicConfig()

#log = logging.getLogger('rpc')
#log.setLevel(logging.DEBUG)

if os.name == 'nt':
	sys.path.insert(0,'.\\GTK-2.0\\lib')
	sys.path.insert(0,'.\\GTK-2.0\\bin')
	sys.path.insert(0,'.\\gs8.54\\bin')
	sys.path.insert(0,'.')
	os.environ['PATH']=".;gs8.54\\bin;GTK-2.0\\lib;GTK-2.0\\bin;" + os.environ['PATH']

from distutils.sysconfig import get_python_lib
terp_path = "/".join([get_python_lib(), 'tinyerp-client'])
sys.path.append(terp_path)

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

import locale, gettext

# for testing cx_Freeze

import atk
import gtk._gtk
import pango

# end testing
APP = 'terp'
DIR = 'po'

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
gettext.install(APP, DIR, unicode=1)
gtk.glade.bindtextdomain(APP, DIR)

import options

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

#pix_file = os.path.join(os.getcwd(),'flag.png')
#if not os.path.isfile(pix_file):
#	pix_file = os.path.join(options.options['path.pixmaps'],'flag.png')
#if not os.path.isfile(pix_file):
#	pix_file = '/usr/share/pixmaps/tinyerp-client/flag.png'
#pixbuf = gtk.gdk.pixbuf_new_from_file(pix_file)
#
#if pixbuf:
#	icon_set = gtk.IconSet (pixbuf)
#	factory.add ('terp-translate', icon_set)

pix_file = os.path.join(os.getcwd(),'icons')
if not os.path.isdir(pix_file):
	pix_file = os.path.join(options.options['path.pixmaps'],'icons')
if not os.path.isdir(pix_file):
	pix_file = '/usr/share/pixmaps/tinyerp-client/icons'

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

common.theme_set()

try:
	win = modules.gui.main.terp_main()
	if not common.terp_survey():
		if options.options.rcexist:
			if options.options['tip.autostart']:
				common.tipoftheday()
			else:
				win.sig_login()
	gtk.main()
except KeyboardInterrupt, e:
	log = logging.getLogger('common')
	log.info(_('Closing Tiny ERP, KeyboardInterrupt'))

