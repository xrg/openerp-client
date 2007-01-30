##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: parser.py 4698 2006-11-27 12:30:44Z ced $
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
from gtk import glade

import tools
import graph

from rpc import RPCProxy
from widget.view import interface

class parser_graph(interface.parser_interface):
	def parse(self, model, root_node, fields):
		attrs = tools.node_attributes(root_node)
		self.title = attrs.get('string', 'Unknown')

		on_write = '' #attrs.get('on_write', '')

		img = gtk.Image()
		img.set_from_stock('gtk-cancel', gtk.ICON_SIZE_BUTTON)
		img.show()


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

		view = graph.ViewGraph(img, model, axis, fields, axis_data, attrs)
		return view, {}, [], on_write


# vim:noexpandtab:

