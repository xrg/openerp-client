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


class ViewWidget(object):
	def __init__(self, parent, widget, widget_name):
		self.view_form = parent
		self.widget = widget
		self.widget._view = self
		self.widget_name = widget_name

	def display(self, model, state='draft'):
		if not model:
			self.widget.state_set('readonly')
			self.widget.display(False)
			return False
		self.widget.state_set(state)
		self.widget.refresh()
		self.widget.display(model[self.widget_name])
	
	def reset(self):
		if 'valid' in self.widget.attrs:
			self.widget.attrs['valid'] = True
		self.widget.refresh()

	def set_value(self, model):
		self.widget.set_value(model[self.widget_name])

	def _get_model(self):
		return self.view_form.screen.current_model

	model = property(_get_model)

	def _get_modelfield(self):
		if self.model:
			return self.model[self.widget_name]

	modelfield = property(_get_modelfield)
