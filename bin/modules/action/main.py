##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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

class main(service.Service):
	def __init__(self, name='action.main'):
		service.Service.__init__(self, name)

	def exec_report(self, name, data):
		datas = data.copy()
		ids = datas['ids']
		del datas['ids']
		if not ids:
			ids =  rpc.session.rpc_exec_auth('/object', 'execute', datas['model'], 'search', [])
			if ids == []:
				common.message(_('Nothing to print!'))
				return False
			datas['id'] = ids[0]
		try:
			report_id = rpc.session.rpc_exec_auth('/report', 'report', name, ids, datas, rpc.session.context)
			state = False
			attempt = 0
			while not state:
				val = rpc.session.rpc_exec_auth('/report', 'report_get', report_id)
				state = val['state']
				if not state:
					time.sleep(1)
					attempt += 1
				if attempt>200:
					common.message(_('Printing aborted, too long delay !'))
					return False
			printer.print_data(val)
		except rpc.rpc_exception, e:
			common.error(_('Error: ')+str(e.type), e.message, e.data)
		return True

	def execute(self, act_id, datas, type=None):
		if type==None:
			res = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.actions.actions', 'read', [act_id], ['type'], rpc.session.context)
			if not len(res):
				raise 'ActionNotFound'
			type=res[0]['type']
		res = rpc.session.rpc_exec_auth('/object', 'execute', type, 'read', [act_id], False, rpc.session.context)[0]
		self._exec_action(res,datas)

	def _exec_action(self, action, datas):
		if 'type' not in action:
			return
		if action['type']=='ir.actions.act_window':
			for key in ('res_id', 'res_model', 'view_type','view_mode'):
				datas[key] = action.get(key, datas.get(key, None))

			if not action.get('domain', False):
				action['domain']='[]'
			context = {'active_id': datas.get('id',False), 'active_ids': datas.get('ids',[])}
			context.update(eval(action.get('context','{}'), context.copy()))

			a = context.copy()
			a['time'] = time
			a['datetime'] = datetime
			domain = tools.expr_eval(action['domain'], a)

			if datas.get('domain', False):
				domain.append(datas['domain'])

			obj = service.LocalService('gui.window')
			obj.create(action['view_id'] and action['view_id'][0], datas['res_model'], datas['res_id'], domain, action['view_type'], datas.get('window',None), context,datas['view_mode'])

			#for key in tools.expr_eval(action.get('context', '{}')).keys():
			#	del rpc.session.context[key]

		elif action['type']=='ir.actions.wizard':
			if 'window' in datas:
				del datas['window']
			wizard.execute(action['wiz_name'], datas)

		elif action['type']=='ir.actions.report.custom':
			datas['report_id'] = action['report_id']
			self.exec_report('custom', datas)

		elif action['type']=='ir.actions.report.xml':
			self.exec_report(action['report_name'], datas)

	def exec_keyword(self, keyword, data={}, adds={}):
		actions = None
		if 'id' in data:
			try:
				id = data.get('id', False) 
				actions = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.values', 'get', 'action', keyword, [(data['model'], id)], False, rpc.session.context)
				actions = map(lambda x: x[2], actions)
			except rpc.rpc_exception, e:
				common.error(_('Error: ')+str(e.type), e.message, e.data)

		keyact = {}
		for action in actions:
			keyact[action['name']] = action
		keyact.update(adds)

		res = common.selection(_('Select your action'), keyact)
		if res:
			(name,action) = res
			self._exec_action(action, data)
			return (name, action)
		elif not len(keyact):
			common.message(_('No action defined!'))
		return False

main()
