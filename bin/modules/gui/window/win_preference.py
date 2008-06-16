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

import gettext

import gtk
from gtk import glade

import rpc

import common
import win_search
import copy
import service
from widget.screen import Screen


class win_preference(object):
	def __init__(self, model, id, preferences, parent=None):
		self.glade = glade.XML(common.terp_path("terp.glade"),'win_preference', gettext.textdomain())
		self.win = self.glade.get_widget('win_preference')
		self.win.set_icon(common.TINYERP_ICON)
		if not parent:
			parent = service.LocalService('gui.main').window
		self.win.set_transient_for(parent)
		self.parent = parent
		self.win.show_all()
		self.id = id
		self.model = model

		fields = {}
		arch = '<?xml version="1.0"?><form string="%s">\n' % (_('Preferences'),)
		for p in preferences:
			arch+='<field name="%s" colspan="4"/>' % (p[1],)
			fields[p[1]] = p[3]
		arch+= '</form>'

		self.screen = Screen(model, view_type=[])
		self.screen.new(default=False)
		self.screen.add_view_custom(arch, fields, display=True)

		default = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.values', 'get', 'meta', False, [(self.model,self.id)], False, rpc.session.context, True, True, False)
		default2 = {}
		self.default = {}
		for d in default:
			default2[d[1]] = d[2]
			self.default[d[1]] = d[0]
		self.screen.current_model.set(default2)

		x,y = self.screen.screen_container.size_get()
		self.screen.widget.set_size_request(x,y)

		vbox = self.glade.get_widget('preference_vbox')
		vbox.pack_start(self.screen.widget)

		self.win.set_title(_('Preference')+' '+model)
		self.win.show_all()

	def run(self, datas={}):
		final = False
		while True:
			res = self.win.run()
			if self.screen.current_model.validate() or (self.states[res]=='end'):
				break
		if res==gtk.RESPONSE_OK:
			final = True

			val = copy.copy(self.screen.get())

			for key in val:
				if val[key]:
					rpc.session.rpc_exec_auth('/object', 'execute', 'ir.values', 'set', 'meta', key, key, [(self.model,self.id)], val[key])
				elif self.default.get(key, False):
					rpc.session.rpc_exec_auth('/common', 'ir_del', self.default[key])
		self.parent.present()
		self.win.destroy()
		return final

