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

import exceptions
import rpc
from rpc import RPCProxy
import field

import signal_event

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
		return self.parent.get()[item]


class ModelRecord(signal_event.signal_event):
	def __init__(self, resource, id, fields, group=None, parent=None, new=False):
		super(ModelRecord, self).__init__()
		self.resource = resource
		self.rpc = RPCProxy(self.resource)
		self.id = id
		self._loaded = False
		self.fields = {}
		self.parent = parent
		self.mgroup = group
		for fname, fvalue in fields.items():
			modelfield = field.ModelField(fvalue['type'])
			fvalue['name'] = fname
			self.fields[fname] = modelfield(self, fvalue)
			if (new and fvalue['type']=='one2many') and (fvalue.get('mode','tree,form').startswith('form')):
				mod = self.fields[fname].internal.model_new(domain=self.fields[fname].domain_get(), context=self.fields[fname].context_get())
				self.fields[fname].internal.model_add(mod)

	def __getitem__(self, name):
		return self.fields.get(name, False)
	
	def __repr__(self):
		return '<ModelRecord %s@%s>' % (self.id, self.resource)

	def __str__(self):
		res = self.__repr__()
		for name, value in self.fields.items():
			res += '\n   - %s : %s' % (name, value.get())
		res += '\n</ModelRecord>'
		return res

	def is_modified(self):
		for name, field in self.fields.items():
			if field.modified:
				return True
		return False

	def fields_get(self):
		fields = {}
		for fname,fval in self.fields.items():
			fields[fname] = fval.attrs
		return fields

	def _check_load(self):
		if not self._loaded:
			self.reload()
			return True
		return False

	def get(self, get_readonly=True):
		self._check_load()
		value = dict([(name, field.get())
					  for name, field in self.fields.items()
					  if get_readonly or not field.attrs.get('readonly', False)])
		return value

	def cancel(self):
		self._loaded = False
		self.reload()

	def save(self, reload=True):
		self._check_load()
		value = self.get(get_readonly=False)
		if not self.id:
			self.id = self.rpc.create(value, self.context_get())
		else:
			if not self.rpc.write([self.id], value, self.context_get()):
				return False
		self._loaded = False
		if reload:
			self.reload()
		return self.id

	def default_get(self, domain=[], context={}):
		if len(self.fields):
			val = self.rpc.default_get(self.fields.keys(), context)
			for d in domain:
				if d[0] in self.fields and d[1]=='=':
					val[d[0]]=d[2]
			self.set_default(val)

	def add_field(self, field_dict):
		modelfield = field.ModelField(field_dict['type'])
		self.fields[field_dict['name']] = modelfield(self, field_dict)
	
	def name_get(self):
		name = self.rpc.name_get([self.id], rpc.session.context)[0]
		return name

	def validate_set(self):
		change = self._check_load()
		for fname in self.fields:
			change = change or not self.fields[fname].attrs.get('valid', True)
			self.fields[fname].attrs['valid'] = True
		if change:
			self.signal('record-changed')
		return change

	def validate(self):
		self._check_load()
		ok = True
		for fname in self.fields:
			if not self.fields[fname].validate():
				self.fields[fname].attrs['valid'] = False
				ok = False
			else:
				self.fields[fname].attrs['valid'] = True
		return ok

	def _get_invalid_fields(self):
		return dict([(fname, field.attrs['string']) for fname, field in self.fields.items() if not field.attrs['valid']])
	invalid_fields = property(_get_invalid_fields)

	def context_get(self):
		return self.mgroup.context

	def get_default(self):
		self._check_load()
		value = dict([(name, field.get_default())
					  for name, field in self.fields.items()])
		return value

	def set_default(self, val):
		for fieldname, value in val.items():
			if fieldname not in self.fields:
				continue
			self.fields[fieldname].set_default(value)
		self._loaded = True
		self.signal('record-changed')

	def set(self, val, modified=False):
		later={}
		for fieldname, value in val.items():
			if fieldname not in self.fields:
				continue
			if isinstance(self.fields[fieldname], field.O2MField):
				later[fieldname]=value
				continue
			self.fields[fieldname].set(value)
			self.fields[fieldname].modified = modified
		for fieldname, value in later.items():
			self.fields[fieldname].set(value)
			self.fields[fieldname].modified = modified
		self._loaded = True
		self.signal('record-changed')

	def reload(self):
		if not self.id:
			return
		c= rpc.session.context.copy()
		c.update(self.context_get())
		value = self.rpc.read([self.id], self.fields.keys(), c)[0]
		self.set(value)

	def expr_eval(self, dom, check_load=True):
		if not isinstance(dom, basestring):
			return dom
		if check_load:
			self._check_load()
		d = {}
		for name, mfield in self.fields.items():
			if not isinstance(mfield, field.O2MField):
				d[name] = mfield.get()

		d['current_date'] = time.strftime('%Y-%m-%d')
		d['time'] = time
		d['context'] = self.context_get()
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
		self.set(response.get('value', {}), modified=True)
		if 'domain' in response:
			for fieldname, value in response['domain'].items():
				if fieldname not in self.fields:
					continue
				self.fields[fieldname].attrs['domain'] = value
		self.signal('record-changed')
	
	def cond_default(self, field, value):
		ir = RPCProxy('ir.values')
		values = ir.get('default', '%s=%s' % (field, value),
						[(self.resource, False)], False, {})
		data = {}
		for index, fname, value in values:
			data[fname] = value
		self.set_default(data)
