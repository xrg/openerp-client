##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: rpc.py 6192 2007-05-08 15:33:14Z bch $
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

import sys,os
import locale
import release
import gettext
import gtk

def setlang(lang=None):
	APP = release.name
	DIR = os.path.join(os.getcwd(), os.path.dirname(sys.argv[0]), 'share/locale')
	if not os.path.isdir(DIR):
		DIR = os.path.join(sys.prefix, 'share/locale')
	if not os.path.isdir(DIR):
		gettext.install(APP, unicode=1)
		return False
	if lang:
		lc, encoding = locale.getdefaultlocale()
		if encoding == 'utf':
			encoding = 'UTF-8'
		try:
			locale.setlocale(locale.LC_ALL, lang+'.'+encoding)
		except:
			pass
		lang = gettext.translation(APP, DIR, languages=lang, fallback=True)
		lang.install(unicode=1)
	else:
		try:
			locale.setlocale(locale.LC_ALL, '')
		except:
			pass
		gettext.bindtextdomain(APP, DIR)
		gettext.textdomain(APP)
		gettext.install(APP, unicode=1)
	gtk.glade.bindtextdomain(APP, DIR)
