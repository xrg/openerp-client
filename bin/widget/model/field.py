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

#
# get: return the values to write to the server
# get_client: return the value for the client widget (form_gtk)
# set: save the value from the server
# set_client: save the value from the widget
#
from rpc import RPCProxy
import rpc
try:
	from sets import Set as set
except ImportError:
	pass

class ModelField(object):
	def __new__(cls, type):
		klass = TYPES.get(type, CharField)
		return klass


class CharField(object):
	def __init__(self, parent, attrs):
		self.parent = parent
		self.attrs = attrs
		self.real_attrs = attrs.copy()
		self.internal = False
		self.modified = False

	def sig_changed(self):
		if self.attrs.get('on_change',False):
			self.parent.on_change(self.attrs['on_change'])
		if self.attrs.get('change_default', False):
			self.parent.cond_default(self.attrs['name'], self.get())

	def domain_get(self):
		dom = self.attrs.get('domain', '[]')
		return self.parent.expr_eval(dom)

	def context_get(self, check_load=True):
		context = {}
		context.update(self.parent.context_get())
		field_context_str = self.attrs.get('context', '{}') or '{}'
		field_context = self.parent.expr_eval('dict(%s)' % field_context_str, check_load=check_load)
		context.update(field_context)
		return context

	def validate(self):
		ok = True
		if self.attrs.get('required', False):
			if not self.internal:
				ok=False
		return ok

	def state_set(self, state):
		if 'states' in self.attrs:
			for key,val in self.real_attrs.items():
				self.attrs[key] = self.real_attrs[key]
			if state in self.attrs['states']:
				for key,val in self.attrs['states'][state]:
					if key=='value':
						self.set(value, test_state=False)
						self.modified = True
					else:
						self.attrs[key] = val

	def set(self, value, test_state=True, modified=False):
		self.internal = value
		return True

	def get(self):
		return self.internal or False

	def set_client(self, value, test_state=True):
		internal = self.internal
		self.set(value, test_state)
		if (internal or False) != (self.internal or False):
			self.modified = True
			self.sig_changed()

	def get_client(self):
		return self.internal or False

	def set_default(self, value):
		return self.set(value)

	def get_default(self):
		return self.get()

class SelectionField(CharField):
	def set(self, value, test_state=True, modified=False):
		if value in [sel[0] for sel in self.attrs['selection']]:
			super(SelectionField, self).set(value, test_state, modified)

class FloatField(CharField):
	def validate(self):
		return True

	def set_client(self, value, test_state=True):
		internal = self.internal
		self.set(value, test_state)
		if abs(float(internal or 0.0) - float(self.internal or 0.0)) >= (10.0**(-self.attrs.get('digits', (12,4))[1])):
			self.modified = True
			self.sig_changed()


class IntegerField(CharField):
	def validate(self):
		return True


# internal = (id, name)
class M2OField(CharField):
	def get(self):
		if self.internal:
			return self.internal[0] or False
		return False

	def get_client(self):
		if self.internal:
			return self.internal[1]
		return False

	def set(self, value, test_state=False, modified=False):
		if value and isinstance(value, (int, str, unicode, long)):
			rpc2 = RPCProxy(self.attrs['relation'])
			result = rpc2.name_get([value], rpc.session.context)
			self.internal = result[0]
		else:
			self.internal = value

	def set_client(self, value, test_state=False):
		internal = self.internal
		self.set(value, test_state)
		if internal != self.internal:
			self.modified = True
			self.sig_changed()

# internal = [id]
class M2MField(CharField):
	def __init__(self, parent, attrs):
		super(M2MField, self).__init__(parent, attrs)
		self.internal = []

	def get(self):
		return [(6, 0, self.internal or [])]

	def get_client(self):
		return self.internal or []

	def set(self, value, test_state=False, modified=False):
		self.internal = value or []

	def set_client(self, value, test_state=False):
		internal = self.internal
		self.set(value, test_state, modified=False)
		if set(internal) != set(value):
			self.modified = True
			self.sig_changed()

	def get_default(self):
		return self.get_client()

# internal = ModelRecordGroup of the related objects
class O2MField(CharField):
	def __init__(self, parent, attrs):
		super(O2MField, self).__init__(parent, attrs)
		from widget.model.group import ModelRecordGroup
		self.context={}
		self.internal = ModelRecordGroup(resource=self.attrs['relation'], fields={}, parent=self.parent, context=self.context_get())

	def _get_modified(self):
		for model in self.internal.models:
			if model.is_modified():
				return True
		if self.internal.model_removed:
			return True
		return False

	def _set_modified(self, value):
		pass
		
	modified = property(_get_modified, _set_modified)

	def _model_changed(self, group, model):
		self.parent.signal('record-changed')

	def get_client(self):
		return self.internal

	def get(self):
		if not self.internal:
			return []
		result = []
		for model in self.internal.models:
			if model.id:
				result.append((1,model.id, model.get()))
			else:
				result.append((0,0, model.get()))
		for id in self.internal.model_removed:
			result.append((2,id, False))
		return result

	def set(self, value, test_state=False, modified=False):
		from widget.model.group import ModelRecordGroup
		self.internal = ModelRecordGroup(resource=self.attrs['relation'], fields={}, parent=self.parent, context=self.context_get(False))
		#self.internal.signal_connect(self.internal, 'model-changed', self._model_changed)
		self.internal.pre_load(value, display=False)
		#self.internal.signal_connect(self.internal, 'model-changed', self._model_changed)

	def set_client(self, value, test_state=False):
		self.set(value, test_state=test_state)

	def set_default(self, value):
		from widget.model.group import ModelRecordGroup
		fields = {}
		if len(value):
			context = self.context_get()
			rpc2 = RPCProxy(self.attrs['relation'])
			fields = rpc2.fields_get(value[0].keys(), context)

		self.internal = ModelRecordGroup(resource=self.attrs['relation'], fields=fields, parent=self.parent)
		#self.internal.signal_connect(self.internal, 'model-changed', self._model_changed)
		mod=None
		for record in value:
			mod = self.internal.model_new(default=False)
			mod.set_default(record)
			self.internal.model_add(mod)
		self.internal.current_model = mod
		#mod.signal('record-changed')
		return True

	def get_default(self):
		res = map(lambda x: x.get_default(), self.internal.models or [])
		return res

class ReferenceField(CharField):
	def get_client(self):
		if self.internal:
			return self.internal
		return False

	def get(self):
		if self.internal:
			return '%s,%d' % (self.internal[0], self.internal[1][0])
		return False

	def set_client(self, value):
		internal = self.internal
		self.internal = value
		if (internal or False) != (self.internal or False):
			self.sig_changed()

	def set(self, value, test_state=False, modified=False):
		if not value:
			self.internal = False
			return
		model, id = value.split(',')
		rpc2 = RPCProxy(model)
		result = rpc2.name_get([id], rpc.session.context)
		if result:
			self.internal = model, result[0]
		else:
			self.internal = False

TYPES = {
	'char' : CharField,
	'integer' : IntegerField,
	'float' : FloatField,
	'many2one' : M2OField,
	'many2many' : M2MField,
	'one2many' : O2MField,
	'reference' : ReferenceField,
	'selection': SelectionField,
}

# vim:noexpandtab:
