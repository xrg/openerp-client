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
		self.name = attrs['name']
		self.internal = False

	def sig_changed(self, model):
		if self.attrs.get('on_change',False):
			model.on_change(self.attrs['on_change'])
		if self.attrs.get('change_default', False):
			model.cond_default(self.attrs['name'], self.get(model))

	def domain_get(self, model):
		dom = self.attrs.get('domain', '[]')
		return model.expr_eval(dom)

	def context_get(self, model, check_load=True, eval=True):
		context = {}
		context.update(self.parent.context)
		field_context_str = self.attrs.get('context', '{}') or '{}'
		if eval:
			field_context = model.expr_eval('dict(%s)' % field_context_str, check_load=check_load)
			context.update(field_context)
		return context

	def validate(self, model):
		ok = True
		if self.attrs.get('required', False):
			if not model.value[self.name]:
				ok=False
		return ok

	def state_set(self, model, state):
		if 'states' in self.attrs:
			for key,val in self.real_attrs.items():
				self.attrs[key] = self.real_attrs[key]
			if state in self.attrs['states']:
				for key,val in self.attrs['states'][state]:
					if key=='value':
						self.set(model, value, test_state=False)
						model.modified = True
					else:
						self.attrs[key] = val

	def set(self, model, value, test_state=True, modified=False):
		model.value[self.name] = value
		return True

	def get(self, model):
		return model.value.get(self.name, False) or False

	def set_client(self, model, value, test_state=True):
		internal = model.value.get(self.name, False)
		self.set(model, value, test_state)
		if (internal or False) != (model.value.get(self.name,False) or False):
			model.modified = True
			self.sig_changed(model)
			model.signal('record-changed', model)

	def get_client(self, model):
		return model.value[self.name] or False

	def set_default(self, model, value):
		return self.set(model, value)

	def get_default(self, model):
		return self.get(model)

	def create(self, model):
		return False

class SelectionField(CharField):
	def set(self, model, value, test_state=True, modified=False):
		if value in [sel[0] for sel in self.attrs['selection']]:
			super(SelectionField, self).set(model, value, test_state, modified)

class FloatField(CharField):
	def validate(self, model):
		return True

	def set_client(self, model, value, test_state=True):
		internal = model.value[self.name]
		self.set(model, value, test_state)
		if abs(float(internal or 0.0) - float(model.value[self.name] or 0.0)) >= (10.0**(-self.attrs.get('digits', (12,4))[1])):
			if not self.attrs.get('readonly', False):
				model.modified = True
				self.sig_changed(model)
				model.signal('record-changed', model)

class IntegerField(CharField):
	def validate(self, model):
		return True


# internal = (id, name)
class M2OField(CharField):
	def create(self, model):
		return False

	def get(self, model):
		if model.value[self.name]:
			return model.value[self.name][0] or False
		return False

	def get_client(self, model):
		#model._check_load()
		if model.value[self.name]:
			return model.value[self.name][1]
		return False

	def set(self, model, value, test_state=False, modified=False):
		if value and isinstance(value, (int, str, unicode, long)):
			rpc2 = RPCProxy(self.attrs['relation'])
			result = rpc2.name_get([value], rpc.session.context)
			model.value[self.name] = result[0]
		else:
			model.value[self.name] = value

	def set_client(self, model, value, test_state=False):
		internal = model.value[self.name]
		self.set(model, value, test_state)
		if internal != model.value[self.name]:
			model.modified = True
			self.sig_changed(model)
			model.signal('record-changed', model)

# internal = [id]
class M2MField(CharField):
	def __init__(self, parent, attrs):
		super(M2MField, self).__init__(parent, attrs)

	def create(self, model):
		return []

	def get(self, model):
		return [(6, 0, model.value[self.name] or [])]

	def get_client(self, model):
		return model.value[self.name] or []

	def set(self, model, value, test_state=False, modified=False):
		model.value[self.name] = value or []

	def set_client(self, model, value, test_state=False):
		internal = model.value[self.name]
		self.set(model, value, test_state, modified=False)
		if set(internal) != set(value):
			model.modified = True
			self.sig_changed(model)
			model.signal('record-changed', model)

	def get_default(self, model):
		return self.get_client(model)

# Decorator printing debugging output.
def debugger(f):
	def debugf(*args,**kwargs):
		print "DEBUG:", f.__name__, args, kwargs
		retv = f(*args,**kwargs)
		print "Function returned:", repr(retv)
		return retv
	return debugf

class debug_function(object):
	def __init__(self, f):
		self.__f = f

	def __call__(self, *args, **kwargs):
		print 'CALL', args, kwargs
		self.__numCalls += 1
		return self.__f(*args, **kwargs)

# internal = ModelRecordGroup of the related objects
class O2MField(CharField):
	def __init__(self, parent, attrs):
		super(O2MField, self).__init__(parent, attrs)
		self.context={}

	def create(self, model):
		from widget.model.group import ModelRecordGroup
		mod = ModelRecordGroup(resource=self.attrs['relation'], fields={}, parent=model, context=self.context_get(model, eval=False))
		mod.signal_connect(mod, 'model-changed', self._model_changed)
		return mod

	def _get_modified(self, model):
		for model in model.value[self.name].models:
			if model.is_modified():
				return True
		if model.value[self.name].model_removed:
			return True
		return False

	def _set_modified(self, model, value):
		pass
		
	modified = property(_get_modified, _set_modified)

	def _model_changed(self, group, model):
		self.sig_changed(model.parent)
		self.parent.signal('record-changed', model)

	def get_client(self, model):
		return model.value[self.name]

	def get(self, model):
		if not model.value[self.name]:
			return []
		result = []
		for model2 in model.value[self.name].models:
			if model2.id:
				result.append((1,model2.id, model2.get()))
			else:
				result.append((0,0, model2.get()))
		for id in model.value[self.name].model_removed:
			result.append((2,id, False))
		return result

	def set(self, model, value, test_state=False, modified=False):
		from widget.model.group import ModelRecordGroup
		mod =  ModelRecordGroup(resource=self.attrs['relation'], fields={}, parent=model, context=self.context_get(model, False))
		mod.signal_connect(mod, 'model-changed', self._model_changed)
		model.value[self.name] =mod
		#self.internal.signal_connect(self.internal, 'model-changed', self._model_changed)
		model.value[self.name].pre_load(value, display=False)
		#self.internal.signal_connect(self.internal, 'model-changed', self._model_changed)

	def set_client(self, model, value, test_state=False):
		self.set(model, value, test_state=test_state)
		model.signal('record-changed', model)

	def set_default(self, model, value):
		from widget.model.group import ModelRecordGroup
		fields = {}
		if value and len(value):
			context = self.context_get(model)
			rpc2 = RPCProxy(self.attrs['relation'])
			fields = rpc2.fields_get(value[0].keys(), context)

		model.value[self.name] = ModelRecordGroup(resource=self.attrs['relation'], fields=fields, parent=model)
		model.value[self.name].signal_connect(model.value[self.name], 'model-changed', self._model_changed)
		mod=None
		for record in (value or []):
			mod = model.value[self.name].model_new(default=False)
			mod.set_default(record)
			model.value[self.name].model_add(mod)
		model.value[self.name].current_model = mod
		#mod.signal('record-changed')
		return True

	def get_default(self, model):
		res = map(lambda x: x.get_default(), model.value[self.name].models or [])
		return res

	def validate(self, model):
		ok = True
		for model2 in model.value[self.name].models:
			if not model2.validate():
				if not model2.is_modified():
					model.value[self.name].models.model_remove(model2)
				else:
					ok = False
		if not super(O2MField, self).validate(model):
			ok = False
		return ok

class ReferenceField(CharField):
	def get_client(self, model):
		if model.value[self.name]:
			return model.value[self.name]
		return False

	def get(self, model):
		if model.value[self.name]:
			return '%s,%d' % (model.value[self.name][0], model.value[self.name][1][0])
		return False

	def set_client(self, model, value):
		internal = model.value[self.name]
		model.value[self.name] = value
		if (internal or False) != (model.value[self.name] or False):
			self.sig_changed(model)
			model.signal('record-changed', model)

	def set(self, model, value, test_state=False, modified=False):
		if not value:
			model.value[self.name] = False
			return
		ref_model, id = value.split(',')
		rpc2 = RPCProxy(ref_model)
		result = rpc2.name_get([id], rpc.session.context)
		if result:
			model.value[self.name] = ref_model, result[0]
		else:
			model.value[self.name] = False

TYPES = {
	'char' : CharField,
	'float_time': FloatField,
	'integer' : IntegerField,
	'float' : FloatField,
	'many2one' : M2OField,
	'many2many' : M2MField,
	'one2many' : O2MField,
	'reference' : ReferenceField,
	'selection': SelectionField,
}

# vim:noexpandtab:
