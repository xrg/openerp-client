##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import gettext

import gtk
from gtk import glade
import common

import rpc

def field_pref_set(field, name, model, value, dependance=[]):
	win_gl = glade.XML(common.terp_path('terp.glade'),'win_field_pref', gettext.textdomain())
	win = win_gl.get_widget('win_field_pref')
	ent = win_gl.get_widget('ent_field')
	ent.set_text(name)
	ent = win_gl.get_widget('ent_domain')
	ent.set_text(model)
	ent = win_gl.get_widget('ent_value')
	ent.set_text((value and str(value)) or '/')

	radio = win_gl.get_widget('radio_user_pref')

	vbox = win_gl.get_widget('pref_vbox')
	widgets = {}
	for (fname,fvalue,rname,rvalue) in dependance:
		widget = gtk.CheckButton(fname+' = '+str(rname))
		widgets[(fvalue,rvalue)] = widget
		vbox.pack_start(widget)
	if not len(dependance):
		vbox.pack_start(gtk.Label(_('Always applicable !')))
	vbox.show_all()

	res = win.run()

	deps = False
	for nv in widgets.keys():
		if widgets[nv].get_active():
			deps = nv[0]+'='+str(nv[1])
			break

	win.destroy()
	if res==gtk.RESPONSE_OK:
		rpc.session.rpc_exec_auth('/object', 'execute', 'ir.values', 'set', 'default', deps, field, [(model,False)], value, True, False, False, radio.get_active())
		return True
	return False

