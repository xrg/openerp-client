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

import locale
import gtk
import tools

from rpc import RPCProxy
from widget.view import interface

class EmptyGraph(object):
	def __init__(self, model, axis, fields, axis_data={}, attrs={}):
		self.widget = gtk.Image()

	def display(self, models):
		pass

class parser_graph(interface.parser_interface):
	def parse(self, model, root_node, fields):
		attrs = tools.node_attributes(root_node)
		self.title = attrs.get('string', 'Unknown')

		on_write = '' #attrs.get('on_write', '')

		axis = []
		axis_data = {}
		for node in root_node.childNodes:
			node_attrs = tools.node_attributes(node)
			if node.localName == 'field':
				axis.append(str(node_attrs['name']))
				axis_data[str(node_attrs['name'])] = node_attrs

		#
		# TODO: parse root_node to fill in axis
		#

		try:
			import graph
			view = graph.ViewGraph(model, axis, fields, axis_data, attrs)
		except Exception, e:
			import common
			import traceback
			import sys
			tb_s = reduce(lambda x, y: x + y, traceback.format_exception(
				sys.exc_type, sys.exc_value, sys.exc_traceback))
			common.error('Graph', _('Can not generate graph !'), details=tb_s,
					parent=self.window)
			view = EmptyGraph(model, axis, fields, axis_data, attrs)
		return view, {}, [], on_write


# vim:noexpandtab:

