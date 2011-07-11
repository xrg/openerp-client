# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from rpc import RPCProxy
import rpc



try:
    set
except NameError:
    from sets import Set as set

import tools

DEFAULT_PAGER_LIMIT = 100

class ModelField(object):
    '''
    get: return the values to write to the server
    get_client: return the value for the client widget (form_gtk)
    set: save the value from the server
    set_client: save the value from the widget
    '''

    def __new__(cls, type):
        klass = TYPES.get(type, CharField)
        return klass


class CharField(object):
    def __init__(self, parent, attrs):
        self.parent = parent
        self.attrs = attrs
        self.name = attrs['name']
        self.internal = False
        self.default_attrs = {}

    def destroy(self):
        del self.parent

    def sig_changed(self, model):
        if self.get_state_attrs(model).get('readonly', False):
            return
        if self.attrs.get('on_change',False):
            model.on_change(self.attrs['on_change'])
        if self.attrs.get('change_default', False):
            model.cond_default(self.attrs['name'], self.get(model))

    def domain_get(self, model):
        dom = self.attrs.get('domain', '[]')
        return model.expr_eval(dom) or []

    def context_get(self, model, check_load=True, eval=True):
        context = {}
        context.update(self.parent.context)
        exclude_ctx = ['set_editable','set_visible','form_view_ref', 'group_by']
        # removing default keys,group_by,search_default of the parent context
        context_own = context.copy()
        for c in context.items():
            if c[0].startswith('default_') or c[0] in exclude_ctx\
                or c[0].startswith('search_default_'):
                del context_own[c[0]]

        field_context_str = self.attrs.get('context', '{}') or '{}'
        if eval:
            field_context = model.expr_eval('dict(%s)' % field_context_str, check_load=check_load)
            context_own.update(field_context)
        return context_own

    def validate(self, model):
        ok = True
        if bool(self.get_state_attrs(model).get('required', 0)):
            if not model.value[self.name]:
                ok=False
        self.get_state_attrs(model)['valid'] = ok
        return ok

    def set(self, model, value, modified=False):
        if isinstance(value, basestring):
            value = value.strip()
        model.value[self.name] = value
        if modified:
            model.modified = True
            model.modified_fields.setdefault(self.name)
        return True

    def get(self, model, check_load=True, readonly=True, modified=False):
        return model.value.get(self.name, False) or False

    def set_client(self, model, value, force_change=False):
        internal = model.value.get(self.name, False)
        self.set(model, value)
        if (internal or False) != (model.value.get(self.name,False) or False):
            model.modified = True
            model.modified_fields.setdefault(self.name)
            self.sig_changed(model)
            model.signal('record-changed', model)

    def get_client(self, model):
        return model.value[self.name] or False

    def set_default(self, model, value):
        res = self.set(model, value)
        model.cond_default(self.attrs['name'], self.get(model))
        if self.attrs.get('on_change',False):
            model.on_change(self.attrs['on_change'])
        return res

    def get_default(self, model):
        return self.get(model)

    def create(self, model):
        return False

    def attrs_set(self, model, widget=None):
        uid = rpc.session.uid
        try:
            attrs_changes = eval(self.attrs.get('attrs',"{}"))
        except:
            attrs_changes = eval(self.attrs.get('attrs',"{}"),model.value)
            for k,v in attrs_changes.items():
                for i in range(0,len(v)):
                   if v[i][2]:
                        if type(v[i][2])==type([]):
                            cond=()
                            cond=v[i][0],v[i][1],v[i][2][0]
                            attrs_changes[k][i]=cond
        for k,v in attrs_changes.items():
            result = True
            result = tools.calc_condition(self, model, v)
            if k == 'invisible' and widget:
                func = ['show_all', 'hide_all'][bool(result)]
                getattr(widget, func)()
                if widget.label_ebox:
                    getattr(widget.label_ebox, func)()
            elif k in ['readonly', 'required'] :
                self.get_state_attrs(model)[k] = result

    def state_set(self, model, state='draft'):
        ro = model.mgroup._readonly
        state_changes = dict(self.attrs.get('states',{}).get(state,[]))
        if 'readonly' in state_changes:
            self.get_state_attrs(model)['readonly'] = state_changes.get('readonly', False)
        else:
            if self.attrs.get('readonly', False) or  ro:
                self.get_state_attrs(model)['readonly'] = True
        if 'required' in state_changes:
            self.get_state_attrs(model)['required'] = state_changes.get('required', False)
        else:
            if self.attrs.get('required', False):
                self.get_state_attrs(model)['required'] = self.attrs['required']
        if 'value' in state_changes:
            self.set(model, state_changes['value'], modified=True)

    def get_state_attrs(self, model):
        if self.name not in model.state_attrs:
            model.state_attrs[self.name] = self.attrs.copy()
        return model.state_attrs[self.name]

class BinaryField(CharField):
    def validate(self, model):
        ok = True
        if bool(self.get_state_attrs(model).get('required', 0)):
            name = "%s.size" % self.name
            if not model.value.get(name, False):
                ok=False
        self.get_state_attrs(model)['valid'] = ok
        return ok

    def set(self, model, value, modified=False):
        model.value[self.name] = value
        if value:
            value = tools.human_size(len(value))
        model.value["%s.size" % self.name] = value
        if modified:
            model.modified = True
            model.modified_fields.setdefault(self.name)
        return True

    def get_client(self, model):
        return model.value.get("%s.size" % self.name, False) 

    def set_client(self, model, value):
        before = self.get(model)
        self.set(model, value)
        if before != self.get(model):
            model.modified = True
            model.modified_fields.setdefault(self.name)
            self.sig_changed(model)
            model.signal('record-changed', model)

class ImageField(CharField):
    
    def set(self, model, value, modified=False):
        model.value[self.name] = value
        if not value:
            model.value[self.name] = ''
        if modified:
            model.modified = True
            model.modified_fields.setdefault(self.name)
        return True


class SelectionField(CharField):
    def set(self, model, value, modified=False):
        value = isinstance(value,(list,tuple)) and len(value) and value[0] or value

        if not self.get_state_attrs(model).get('required', False) and value is None:
            super(SelectionField, self).set(model, value, modified)

        if value in [sel[0] for sel in self.attrs['selection']]:
            super(SelectionField, self).set(model, value, modified)

class FloatField(CharField):
    def validate(self, model):
        self.get_state_attrs(model)['valid'] = True
        return True

    def set_client(self, model, value, force_change=False):
        internal = model.value[self.name]
        self.set(model, value)
        if abs(float(internal or 0.0) - float(model.value[self.name] or 0.0)) >= (10.0**(-1-int(self.attrs.get('digits', (12,4))[1]))):
            if not self.get_state_attrs(model).get('readonly', False):
                model.modified = True
                model.modified_fields.setdefault(self.name)
                self.sig_changed(model)
                model.signal('record-changed', model)

class IntegerField(CharField):
    def get(self, model, check_load=True, readonly=True, modified=False):
        return model.value.get(self.name, 0) or 0

    def get_client(self, model):
        return model.value[self.name] or 0

    def validate(self, model):
        self.get_state_attrs(model)['valid'] = True
        return True

    def set_client(self, model, value, force_change=False):
        internal = model.value.get(self.name, False)
        self.set(model, value)
        if int(internal or False) != (model.value.get(self.name,False) or False):
            model.modified = True
            model.modified_fields.setdefault(self.name)
            self.sig_changed(model)
            model.signal('record-changed', model)


class M2OField(CharField):
    '''
    internal = (id, name)
    '''

    def create(self, model):
        return False

    def get(self, model, check_load=True, readonly=True, modified=False):
        if model.value[self.name]:
            return model.value[self.name][0] or False
        return False

    def get_client(self, model):
        #model._check_load()
        if model.value[self.name]:
            return model.value[self.name][1]
        return False

    def set(self, model, value, modified=False):
        if value and isinstance(value, (int, str, unicode, long)):
            rpc2 = RPCProxy(self.attrs['relation'])
            result = rpc2.name_get([value], rpc.session.context)
            model.value[self.name] = result and result[0] or ''
        else:
            model.value[self.name] = value
        if modified:
            model.modified = True
            model.modified_fields.setdefault(self.name)

    def set_client(self, model, value, force_change=False):
        internal = model.value[self.name]
        self.set(model, value)
        if internal != model.value[self.name]:
            model.modified = True
            model.modified_fields.setdefault(self.name)
            self.sig_changed(model)
            model.signal('record-changed', model)
        elif force_change:
            self.sig_changed(model)

class M2MField(CharField):
    '''
    internal = [id]
    '''

    def __init__(self, parent, attrs):
        super(M2MField, self).__init__(parent, attrs)
        self.limit = DEFAULT_PAGER_LIMIT

    def create(self, model):
        return []

    def get(self, model, check_load=True, readonly=True, modified=False):
        if self.name in model.pager_cache:
            return [(6, 0, model.pager_cache[self.name] or [])]
        return []

    def get_client(self, model):
        res = []
        if self.name in model.pager_cache:
            res = model.pager_cache[self.name]
        return res or model.value[self.name] or []

    def set(self, model, value, modified=False):
        ## The case where M2M may appear in a domain as string
        ## eg: if I have a domain on partner list view as
        ## [('categ_id','=','supplier')]
        if value and isinstance(value[0], (str, unicode)):
            rpc2 = RPCProxy(self.attrs['relation'])
            result = []
            for val in value:
                    result += rpc2.name_search(val, [], '=', rpc.session.context)
            value = map(lambda x:x[0], result)
        model.value[self.name] = value and value[:self.limit] or []
        model.pager_cache[self.name] = value or []
        if modified:
            model.modified = True
            model.modified_fields.setdefault(self.name)

    def set_client(self, model, value, force_change=False):
        internal = model.pager_cache.get(self.name, [])
        self.set(model, value, modified=False)
        if model.is_m2m_modified or set(internal) != set(value):
            model.is_m2m_modified = False
            model.modified = True
            model.modified_fields.setdefault(self.name)
            self.sig_changed(model)
            model.signal('record-changed', model)

    def get_default(self, model):
        return self.get_client(model)


class O2MField(CharField):
    '''
    internal = ModelRecordGroup of the related objects
    '''

    def __init__(self, parent, attrs):
        super(O2MField, self).__init__(parent, attrs)
        self.context={}
        self.limit = DEFAULT_PAGER_LIMIT

    def create(self, model):
        from widget.model.group import ModelRecordGroup
        mod = ModelRecordGroup(resource=self.attrs['relation'], fields={}, parent=model)
        mod.signal_connect(mod, 'model-changed', self._model_changed)
        return mod

    def _model_changed(self, group, model):
        model.parent.modified = True
        model.parent.modified_fields.setdefault(self.name)
        self.sig_changed(model.parent)
        self.parent.signal('record-changed', model)

    def get_client(self, model):
        return model.value[self.name]

    def get(self, model, check_load=True, readonly=True, modified=False):
        if not model.value[self.name]:
            return []
        result = []
        for model2 in model.value[self.name].models:
            if (modified and not model2.is_modified()) or \
                    (not model2.id and not model2.is_modified()):
                continue
            if model2.id:
                result.append((1,model2.id, model2.get(check_load=check_load, get_readonly=readonly)))
            else:
                result.append((0,0, model2.get(check_load=check_load, get_readonly=readonly)))
        for model2 in model.value[self.name].models_removed:
            result.append((2, model2.id, False))
        return result

    def set(self, model, value, modified=False):
        if value and not isinstance(value[0], int):
            model = self.set_default(model, value)
            return
        from widget.model.group import ModelRecordGroup
        mod =  ModelRecordGroup(resource=self.attrs['relation'], fields={}, parent=model)
        mod.signal_connect(mod, 'model-changed', self._model_changed)
        model.value[self.name] = mod
        #self.internal.signal_connect(self.internal, 'model-changed', self._model_changed)
        if value:
            value = value[:self.limit]
        model.value[self.name].pre_load(value, display=False)
        #self.internal.signal_connect(self.internal, 'model-changed', self._model_changed)

    def set_client(self, model, value, force_change=False):
        self.set(model, value)
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
        mod = None
        for record in (value or []):
            mod = model.value[self.name].model_new(default=False)
            mod.set_default(record)
            model.value[self.name].model_add(mod)
            mod.modified = True
        model.value[self.name].current_model = mod
        if mod:
            mod.signal('record-changed')
        return model

    def get_default(self, model):
        res = map(lambda x: x.get_default(), model.value[self.name].models or [])
        return res

    def validate(self, model):
        ok = True
        for model2 in model.value[self.name].models:
            if not model2.validate():
                ok = False
        if not super(O2MField, self).validate(model):
            ok = False
        self.get_state_attrs(model)['valid'] = ok
        return ok

class ReferenceField(CharField):

    def validate(self, model):
        ok = True
        if bool(self.get_state_attrs(model).get('required', 0)):
            value = model.value[self.name]
            if value:
                model_name, (id, name) = value
                if int(id) < 1:
                    ok = False
            else:
                ok = False
        self.get_state_attrs(model)['valid'] = ok
        return ok

    def get_client(self, model):
        if model.value[self.name]:
            return model.value[self.name]
        return False

    def get(self, model, check_load=True, readonly=True, modified=False):
        if model.value[self.name]:
            val = model.value[self.name]
            if not isinstance(val, (tuple, list)):
                val = eval(val)
            if val and val[0] and val[1][0]:
                return '%s,%d' % (val[0], val[1][0])
        return False

    def set_client(self, model, value, force_change=False):
        internal = model.value[self.name]
        model.value[self.name] = value
        if (internal or False) != (model.value[self.name] or False):
            model.modified = True
            model.modified_fields.setdefault(self.name)
            self.sig_changed(model)
            model.signal('record-changed', model)

    def set(self, model, value, modified=False):
        if not value:
            model.value[self.name] = False
            return
        ref_model, id = value.split(',')
        if id:
            id = int(id)
        rpc2 = RPCProxy(ref_model)
        result = rpc2.name_get([id], rpc.session.context)
        if result:
            model.value[self.name] = ref_model, result[0]
        else:
            model.value[self.name] = False
        if modified:
            model.modified = True
            model.modified_fields.setdefault(self.name)

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
    'boolean': IntegerField,
    'image': ImageField,
    'binary': BinaryField,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

