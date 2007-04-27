##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: list.py 4411 2006-11-02 23:59:17Z pinky $
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

import gobject
import gtk

class ViewGraph(object):

	def __init__(self, screen, view, children={}, buttons={}, toolbar=None):
		self.screen = screen
		self.view_type = 'graph'
		#self.model_add_new = True
		self.view = view
		self.widget = view.widget
		self.widget.screen = screen

	def cancel(self):
		pass

	def __str__(self):
		return 'ViewGraph (%s)' % self.screen.resource

	def __getitem__(self, name):
		return None

	def destroy(self):
		self.widget.destroy()
		del self.screen
		del self.widget

	def set_value(self):
		pass

	def reset(self):
		pass

	#
	# self.widget.set_model(self.store) could be removed if the store
	# has not changed -> better ergonomy. To test
	#
	def display(self):
		self.view.display(self.screen.models)
		return None

	def signal_record_changed(self, *args):
		pass

	def sel_ids_get(self):
		return []

	def on_change(self, callback):
		pass

	def unset_editable(self):
		pass

	def set_cursor(self):
		pass
