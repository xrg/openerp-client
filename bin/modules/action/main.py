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

import os, time, base64, datetime

import service
import rpc

import wizard
import printer

import common
import tools
from widget.view.form_gtk.many2one import dialog

class main(service.Service):
    def __init__(self, name='action.main'):
        service.Service.__init__(self, name)

    def exec_report(self, name, data, context={}):
        datas = data.copy()
        ids = datas['ids']
        del datas['ids']
        if not ids:
            ids =  rpc.session.rpc_exec_auth('/object', 'execute', datas['model'], 'search', [])
            if ids == []:
                common.message(_('Nothing to print!'))
                return False
            datas['id'] = ids[0]
        ctx = rpc.session.context.copy()
        ctx.update(context)
        report_id = rpc.session.rpc_exec_auth('/report', 'report', name, ids, datas, ctx)
        state = False
        attempt = 0
        while not state:
            val = rpc.session.rpc_exec_auth('/report', 'report_get', report_id)
            if not val:
                return False
            state = val['state']
            if not state:
                time.sleep(1)
                attempt += 1
            if attempt>200:
                common.message(_('Printing aborted, too long delay !'))
                return False
        printer.print_data(val)
        return True

    def execute(self, act_id, datas, type=None, context={}):
        ctx = rpc.session.context.copy()
        ctx.update(context)
        if type==None:
            res = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.actions.actions', 'read', [act_id], ['type'], ctx)
            if not len(res):
                raise Exception, 'ActionNotFound'
            type=res[0]['type']

        if type == 'ir.actions.act_window':
            # the field 'views' is transfered as a binary field
            ctx['get_binary_size'] = False
        res = rpc.session.rpc_exec_auth('/object', 'execute', type, 'read', [act_id], False, ctx)[0]
        self._exec_action(res,datas,context)

    def _exec_action(self, action, datas, context={}):
        if 'type' not in action:
            return
        if action['type']=='ir.actions.act_window':
            for key in ('res_id', 'res_model', 'view_type', 'view_mode',
                    'limit', 'auto_refresh'):
                datas[key] = action.get(key, datas.get(key, None))

            if datas['limit'] is None or datas['limit'] == 0:
                datas['limit'] = 80

            view_ids=False
            if action.get('views', []):
                view_ids=[x[0] for x in action['views']]
                datas['view_mode']=",".join([x[1] for x in action['views']])
            elif action.get('view_id', False):
                view_ids=[action['view_id'][0]]

            if not action.get('domain', False):
                action['domain']='[]'
            ctx = {'active_id': datas.get('id',False), 'active_ids': datas.get('ids',[])}
            ctx.update(tools.expr_eval(action.get('context','{}'), ctx.copy()))
            ctx.update(context)

            a = ctx.copy()
            a['time'] = time
            a['datetime'] = datetime
            domain = tools.expr_eval(action['domain'], a)

            if datas.get('domain', False):
                domain.append(datas['domain'])
            if action.get('target', False)=='new':
                dia = dialog(datas['res_model'], window=datas.get('window',None), domain=domain, context=ctx, view_ids=view_ids,target=True, view_type=datas.get('view_mode', 'tree').split(','))
                if dia.dia.get_has_separator():
                    dia.dia.set_has_separator(False)
                dia.run()
                dia.destroy()
            else:
                obj = service.LocalService('gui.window')
                obj.create(view_ids, datas['res_model'], datas['res_id'], domain,
                        action['view_type'], datas.get('window',None), ctx,
                        datas['view_mode'], name=action.get('name', False),
                        limit=datas['limit'], auto_refresh=datas['auto_refresh'])

        elif action['type']=='ir.actions.server':
            ctx = context.copy()
            ctx.update({'active_id': datas.get('id',False), 'active_ids': datas.get('ids',[])})
            res = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.actions.server', 'run', [action['id']], ctx)
            if res:
                self._exec_action(res, datas, context)

        elif action['type']=='ir.actions.wizard':
            win=None
            if 'window' in datas:
                win=datas['window']
                del datas['window']
            wizard.execute(action['wiz_name'], datas, parent=win, context=context)

        elif action['type']=='ir.actions.report.custom':
            if 'window' in datas:
                win=datas['window']
                del datas['window']
            datas['report_id'] = action['report_id']
            self.exec_report('custom', datas)

        elif action['type']=='ir.actions.report.xml':
            if 'window' in datas:
                win=datas['window']
                del datas['window']
            self.exec_report(action['report_name'], datas)

        elif action['type']=='ir.actions.act_url':
            tools.launch_browser(action.get('url',''))

    def exec_keyword(self, keyword, data={}, adds={}, context={}, warning=True):
        actions = None
        if 'id' in data:
            try:
                id = data.get('id', False)
                ctx = rpc.session.context.copy()
                ctx['get_binary_size'] = False
                actions = rpc.session.rpc_exec_auth('/object', 'execute',
                        'ir.values', 'get', 'action', keyword,
                        [(data['model'], id)], False, ctx)
                actions = map(lambda x: x[2], actions)
            except rpc.rpc_exception, e:
#               common.error(_('Error: ')+str(e.type), e.message, e.data)
                return False

        keyact = {}
        for action in actions:
            keyact[action['name']] = action
        keyact.update(adds)

        res = common.selection(_('Select your action'), keyact)
        if res:
            (name,action) = res
            self._exec_action(action, data, context=context)
            return (name, action)
        return False

main()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

