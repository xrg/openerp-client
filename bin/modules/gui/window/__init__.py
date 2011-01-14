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
import rpc

import common
import form
import tree


class window_int(object):
    def __init__(self, view, datas):
        self.name = datas.get('name', _('Unknown Window'))


class window(service.Service):
    def __init__(self, name='gui.window'):
        service.Service.__init__(self, name)
    def create(self, view_ids, model, res_id=False, domain=None,
            view_type='form', window=None, context=None, mode=None, name=False,
            limit=80, auto_refresh=False):
        if context is None:
            context = {}
        context.update(rpc.session.context)

        if view_type=='form':
            mode = (mode or 'form,tree').split(',')
            win = form.form(model, res_id, domain, view_type=mode,
                    view_ids = (view_ids or []), window=window,
                    context=context, name=name, limit=limit,
                    auto_refresh=auto_refresh)
            spool = service.LocalService('spool')
            spool.publish('gui.window', win, {})
        elif view_type=='tree':
            if view_ids and view_ids[0]:
                view_base =  rpc.session.rpc_exec_auth('/object', 'execute',
                        'ir.ui.view', 'read', [view_ids[0]],
                        ['model', 'type'], context)[0]
                model = view_base['model']
                view = rpc.session.rpc_exec_auth('/object', 'execute',
                        view_base['model'], 'fields_view_get', view_ids[0],
                        view_base['type'],context)
            else:
                view = rpc.session.rpc_exec_auth('/object', 'execute', model,
                        'fields_view_get', False, view_type, context)

            win = tree.tree(view, model, res_id, domain, context,
                    window=window, name=name)
            spool = service.LocalService('spool')
            spool.publish('gui.window', win, {})
        else:
            import logging
            log = logging.getLogger('view')
            log.error('unknown view type: '+view_type)
            del log

window()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

