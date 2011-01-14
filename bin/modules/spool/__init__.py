# -*- encoding: utf-8 -*-
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

class spool(service.Service):
    def __init__(self, name='spool'):
        service.Service.__init__(self, name, '*')
        self.obj_sub = {}
        self.report = {}

    def publish(self, name, obj, datas, trigger=True):
        if name not in self.report:
            self.report[name]=[]
        self.report[name].append((obj, datas))
        if trigger:
            return self.trigger(name)
        return 0

    def subscribe(self, name, method, datas={}):
        if name not in self.obj_sub:
            self.obj_sub[name]=[]
        self.obj_sub[name].append( (method, datas) )

    def trigger(self, name):
        nbr = 0
        while len(self.report[name]):
            (obj, datas) = self.report[name].pop()
            if name in self.obj_sub:
                for i in self.obj_sub[name]:
                    new_datas = datas.copy()
                    new_datas.update(i[1])
                    i[0](obj, new_datas)
                    nbr +=1
        return nbr
spool()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

