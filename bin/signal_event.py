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

class signal_event(object):
	def __init__(self):
		self.__connects = {}

	def signal(self, signal, signal_data=None):
		for fnct,data,key in self.__connects.get(signal, []):
			#print "SIGNAL", signal, fnct
			fnct(self, signal_data, *data)
		return True

	def signal_connect(self, key, signal, fnct, *data):
		self.__connects.setdefault(signal, [])
		self.__connects[signal].append((fnct, data, key))
		return True

	def signal_unconnect(self, key, signal=None):
		if not signal:
			signal = self.__connects.keys()
		else:
			signal = [signal]
		for sig in signal:
			i=0
			while i<len(self.__connects[sig]):
				if self.__connects[sig][i][2]==key:
					del self.__connects[sig][i]
				else:
					i+=1
		return True



