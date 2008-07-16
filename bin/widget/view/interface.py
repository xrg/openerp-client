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

import service

class parser_interface(object):
	def __init__(self, window=None, parent=None, attrs={}, screen=None):
		if window is None:
			window = service.LocalService('gui.main').window
		self.window = window
		self.parent = parent
		self.attrs = attrs
		self.title = None
		self.buttons = {}
		self.screen = screen

class parser_view(object):
	def __init__(self, window, screen, widget, children=None, state_aware_widgets=None, toolbar=None):
		if window is None:
			window = service.LocalService('gui.main').window
		self.window = window
		self.screen = screen
		self.widget = widget
		self.state_aware_widgets = state_aware_widgets or []
