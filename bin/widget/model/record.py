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

import re
import time
import common
import rpc
from rpc import RPCProxy
import field
import signal_event
import gtk
import gettext
import service
from gtk import glade
import tools
from field import O2MField

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
        self.resource = str(resource)
        self.rpc = RPCProxy(self.resource)
        self.id = id
        self._loaded = False
        self.parent = parent
        self.mgroup = group
        self.value = {}
        self.state_attrs = {}
        self.modified = False
        self.modified_fields = {}
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

    def is_modified(self):
        return self.modified
    
    def is_wizard(self):
        return self.mgroup.is_wizard

    def fields_get(self):
        return self.mgroup.mfields

    def _check_load(self):
        if not self._loaded:
            self.reload()
            return True
        return False

    def get(self, get_readonly=True, includeid=False, check_load=True, get_modifiedonly=False):
        if check_load:
            self._check_load()
        value = []
        for name, field in self.mgroup.mfields.items():
            if (get_readonly or not field.get_state_attrs(self).get('readonly', False)) \
                and (not get_modifiedonly or (field.name in self.modified_fields or isinstance(field, O2MField))):
                    value.append((name, field.get(self, readonly=get_readonly,
                        modified=get_modifiedonly)))
        value = dict(value)
        if includeid:
            value['id'] = self.id
        return value

    def cancel(self):
        self._loaded = False
        self.reload()

    def save(self, reload=True):
        self._check_load()
        if not self.id:
            value = self.get(get_readonly=False)
            self.id = self.rpc.create(value, self.context_get())
        else:
            if not self.is_modified():
                return self.id
            value = self.get(get_readonly=False, get_modifiedonly=True)
            context= self.context_get()
            context= context.copy()
            context['read_delta']= time.time()-self.read_time
            if not rpc.session.rpc_exec_auth('/object', 'execute', self.resource, 'write', [self.id], value, context):
                return False
        self._loaded = False
        if reload:
            self.reload()
        return self.id

    def default_get(self, domain=[], context={}):
        if len(self.mgroup.fields):
            val = self.rpc.default_get(self.mgroup.fields.keys(), context)
            for d in domain:
                if d[0] in self.mgroup.fields:
                    if d[1] == '=':
                        val[d[0]] = d[2]
                    if d[1] == 'in' and len(d[2]) == 1:
                        val[d[0]] = d[2][0]
            self.set_default(val)

    def name_get(self):
        name = self.rpc.name_get([self.id], rpc.session.context)[0]
        return name

    def validate_set(self):
        change = self._check_load()
        for fname in self.mgroup.mfields:
            field = self.mgroup.mfields[fname]
            change = change or not field.get_state_attrs(self).get('valid', True)
            field.get_state_attrs(self)['valid'] = True
        if change:
            self.signal('record-changed')
        return change

    def validate(self):
        self._check_load()
        ok = True
        for fname in self.mgroup.mfields:
            if not self.mgroup.mfields[fname].validate(self):
                ok = False
        return ok

    def _get_invalid_fields(self):
        res = []
        for fname, field in self.mgroup.mfields.items():
            if not field.get_state_attrs(self).get('valid', True):
                res.append((fname, field.attrs['string']))
        return dict(res)
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
        for fieldname, value in val.items():
            if fieldname not in self.mgroup.mfields:
                continue
            if isinstance(self.mgroup.mfields[fieldname], field.O2MField):
                later[fieldname]=value
                continue
            self.mgroup.mfields[fieldname].set(self, value, modified=modified)
        for fieldname, value in later.items():
            self.mgroup.mfields[fieldname].set(self, value, modified=modified)
        self._loaded = True
        self.modified = modified
        if not self.modified:
            self.modified_fields = {}
        if signal:
            self.signal('record-changed')
        
    def reload(self):
        if not self.id:
            return
        c= rpc.session.context.copy()
        c.update(self.context_get())
        c['bin_size'] = True
        res = self.rpc.read([self.id], self.mgroup.mfields.keys(), c)
        if res:
            value = res[0]
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
        val = tools.expr_eval(dom, d)
        return val

    #XXX Shoud use changes of attributes (ro, ...)
    def on_change(self, callback):
        match = re.match('^(.*?)\((.*)\)$', callback)
        if not match:
            raise Exception, 'ERROR: Wrong on_change trigger: %s' % callback
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
            warning=response.get('warning',{})			
            if warning:
                common.warning(warning['message'], warning['title'])
        self.signal('record-changed')
    
    def on_change_attrs(self, callback):
        self.signal('attrs-changed')

    def cond_default(self, field, value):
        ir = RPCProxy('ir.values')
        values = ir.get('default', '%s=%s' % (field, value),
                        [(self.resource, False)], False, {})
        data = {}
        for index, fname, value in values:
            data[fname] = value
        self.set_default(data)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

