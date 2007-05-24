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

import re
import time
import common
import exceptions
import rpc
from rpc import RPCProxy
import field
import signal_event
import gtk
import gettext
import service
from gtk import glade

class EvalEnvironment(object):
	def __init__(self, parent):
		self.parent = parent

	def __getattr__(self, item):
		if item=='parent' and self.parent.parent:
			return EvalEnvironment(self.parent.parent)
		if item=="current_date":
			return time.strftime('%Y-%m-%d')
		if item=="time":
			return time
		return self.parent.get(includeid=True)[item]


class ModelRecord(signal_event.signal_event):
	def __init__(self, resource, id, group=None, parent=None, new=False ):
		super(ModelRecord, self).__init__()
		self.resource = resource
		self.rpc = RPCProxy(self.resource)
		self.id = id
		self._loaded = False
		self.parent = parent
		self.mgroup = group
		self.value = {}
		self.modified = False
		self.read_time = time.time()
		for key,val in self.mgroup.mfields.items():
			self.value[key] = val.create(self)
			if (new and val.attrs['type']=='one2many') and (val.attrs.get('mode','tree,form').startswith('form')):
				mod = self.value[key].model_new()
				self.value[key].model_add(mod)

	def __getitem__(self, name):
		return self.mgroup.mfields.get(name, False)
	
	def __repr__(self):
		return '<ModelRecord %s@%s>' % (self.id, self.resource)

# 	def __str__(self):
# 		res = self.__repr__()
# 		for name, value in self.fields_get().items():
# 			res += '\n   - %s : %s' % (name, value.get())
# 		res += '\n</ModelRecord>'
# 		return res

	def is_modified(self):
		return self.modified

	def fields_get(self):
		return self.mgroup.mfields

	def _check_load(self):
		if not self._loaded:
			self.reload()
			return True
		return False

	def get(self, get_readonly=True, includeid=False, check_load=True):
		if check_load:
			self._check_load()
		value = dict([(name, field.get(self))
					  for name, field in self.mgroup.mfields.items()
					  if get_readonly or not field.attrs.get('readonly', False)])
		if includeid:
			value['id'] = self.id
		return value

	def cancel(self):
		self._loaded = False
		self.reload()

	def save(self, reload=True,check_delta=True):
		self._check_load()
		value = self.get(get_readonly=False)
		if not self.id:
			self.id = self.rpc.create(value, self.context_get())
		else:
			context= self.context_get()
			if check_delta:
				context= context.copy()
				context['read_delta']= time.time()-self.read_time
			try:
				if not rpc.session.rpc_exec_auth_wo('/object', 'execute', self.resource, 'write', [self.id], value, context):
					return False
				self.read_time = time.time()
			except rpc.rpc_exception, e:
				if e.message=='ConcurrencyException':
					glade_win = glade.XML(common.terp_path("terp.glade"),'dialog_concurrency_exception',gettext.textdomain())
					dialog = glade_win.get_widget('dialog_concurrency_exception')

					resp= dialog.run()
					dialog.destroy()

					if resp == gtk.RESPONSE_OK:
						self.save(check_delta= False)
					if resp == gtk.RESPONSE_APPLY:
						reload = False
						obj = service.LocalService('gui.window')
						obj.create(False, self.resource, self.id, [], 'form', None, context,'form,tree')
				else:
					common.error(_('Application Error'), e.code, e.type)

		self._loaded = False
		if reload:
			self.reload()
		return self.id

	def default_get(self, domain=[], context={}):
		if len(self.mgroup.fields):
			val = self.rpc.default_get(self.mgroup.fields.keys(), context)
			for d in domain:
				if d[0] in self.mgroup.fields and d[1]=='=':
					val[d[0]]=d[2]
			self.set_default(val)

	def name_get(self):
		name = self.rpc.name_get([self.id], rpc.session.context)[0]
		return name

	def validate_set(self):
		change = self._check_load()
		for fname in self.mgroup.mfields:
			change = change or not self.mgroup.mfields[fname].attrs.get('valid', True)
			self.mgroup.mfields[fname].attrs['valid'] = True
		if change:
			self.signal('record-changed')
		return change

	def validate(self):
		self._check_load()
		ok = True
		for fname in self.mgroup.mfields:
			if not self.mgroup.mfields[fname].validate(self):
				self.mgroup.mfields[fname].attrs['valid'] = False
				ok = False
			else:
				self.mgroup.mfields[fname].attrs['valid'] = True
		return ok

	def _get_invalid_fields(self):
		return dict([(fname, field.attrs['string']) for fname, field in self.mgroup.mfields.items() if not field.attrs['valid']])
	invalid_fields = property(_get_invalid_fields)

	def context_get(self):
		return self.mgroup.context

	def get_default(self):
		self._check_load()
		value = dict([(name, field.get_default(self))
					  for name, field in self.mgroup.mfields.items()])
		return value

	def set_default(self, val):
		for fieldname, value in val.items():
			if fieldname not in self.mgroup.mfields:
				continue
			self.mgroup.mfields[fieldname].set_default(self, value)
		self._loaded = True
		self.signal('record-changed')

	def set(self, val, modified=False, signal=True):
		later={}
		self.modified = modified
		for fieldname, value in val.items():
			if fieldname not in self.mgroup.mfields:
				continue
			if isinstance(self.mgroup.mfields[fieldname], field.O2MField):
				later[fieldname]=value
				continue
			self.mgroup.mfields[fieldname].set(self, value)
		for fieldname, value in later.items():
			self.mgroup.mfields[fieldname].set(self, value)
		self._loaded = True
		if signal:
			self.signal('record-changed')
		
	def reload(self):
		if not self.id:
			return
		c= rpc.session.context.copy()
		c.update(self.context_get())
		value = self.rpc.read([self.id], self.mgroup.mfields.keys(), c)[0]
		self.read_time= time.time()
		self.set(value)

	def expr_eval(self, dom, check_load=True):
		if not isinstance(dom, basestring):
			return dom
		if check_load:
			self._check_load()
		d = {}
		for name, mfield in self.mgroup.mfields.items():
			d[name] = mfield.get(self, check_load=check_load)

		d['current_date'] = time.strftime('%Y-%m-%d')
		d['time'] = time
		d['context'] = self.context_get()
		d['active_id'] = self.id
		if self.parent:
			d['parent'] = EvalEnvironment(self.parent)
		val = eval(dom, d)
		return val

	#
	# Shoud use changes of attributes (ro, ...)
	#
	def on_change(self, callback):
		match = re.match('^(.*?)\((.*)\)$', callback)
		if not match:
			raise 'ERROR: Wrong on_change trigger: %s' % callback
		func_name = match.group(1)
		arg_names = [n.strip() for n in match.group(2).split(',')]
		args = [self.expr_eval(arg) for arg in arg_names]
		ids = self.id and [self.id] or []
		response = getattr(self.rpc, func_name)(ids, *args)
		if response:
			self.set(response.get('value', {}), modified=True)
			if 'domain' in response:
				for fieldname, value in response['domain'].items():
					if fieldname not in self.mgroup.mfields:
						continue
					self.mgroup.mfields[fieldname].attrs['domain'] = value
		self.signal('record-changed')
	
	def cond_default(self, field, value):
		ir = RPCProxy('ir.values')
		values = ir.get('default', '%s=%s' % (field, value),
						[(self.resource, False)], False, {})
		data = {}
		for index, fname, value in values:
			data[fname] = value
		self.set_default(data)
