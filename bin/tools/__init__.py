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

import datetime
import operator
import logging
import locale
import os
import time
from dateutil.relativedelta import relativedelta

import rpc

if os.name == 'nt':
    import win32

def expr_eval(string, context=None):
    if context is None:
        context = {}
    context.update(
        uid = rpc.session.uid,
        current_date = time.strftime('%Y-%m-%d'),
        time = time,
        datetime = datetime,
        relativedelta = relativedelta,
    )
    if isinstance(string, basestring):
        string = string.strip()
        if not string:
            return {}
        # sometimes the server returns the active_id  as a string
        string = string.replace("'active_id'","active_id")
        try:
            temp = eval(string, context)
        except Exception, e:
            logging.getLogger('tools.expr_eval').exception(string)
            return {}
        return temp
    else:
        return string

def launch_browser(url):
    import webbrowser
    import sys
    if sys.platform == 'win32':
        webbrowser.open(url.decode('utf-8'))
    else:
        import os
        pid = os.fork()
        if not pid:
            pid = os.fork()
            if not pid:
                webbrowser.open(url)
            sys.exit(0)
        os.wait()

def node_attributes(node):
    attrs = dict(node.attrib)
    if attrs is None:
        return {}
    if 'digits' in attrs and isinstance(attrs['digits'],(str,unicode)):
        attrs['digits'] = eval(attrs['digits'])
    return attrs

#FIXME use spaces
def calc_condition(self, model, cond):
    cond_main = cond[:]
    try:
        return ConditionExpr(cond).eval(model)
    except Exception, e:
        import common
        common.error('Wrong attrs Implementation!','You have wrongly specified conditions in attrs %s' %(cond_main,))

class ConditionExpr(object):

    OPERAND_MAPPER = {'<>': '!=', '==': '='}

    def __init__(self, condition):
        self.cond = condition

    def eval(self, model):
        if model:
            eval_stack = [] # Stack used for evaluation
            ops = ['=','!=','<','>','<=','>=','in','not in','<>','==']

            def is_operand(cond): # Method to check the Operands
                if (len(cond)==3 and cond[1] in ops) or isinstance(cond,bool):
                    return True
                else:
                    return False

            def evaluate(cond): # Method to evaluate the conditions
                if isinstance(cond,bool):
                    return cond
                left, oper, right = cond
                if not model or not left in model.mgroup.fields:  #check that the field exist
                    return False

                oper = self.OPERAND_MAPPER.get(oper.lower(), oper)
                if oper == '=':
                    res = operator.eq(model[left].get(model),right)
                elif oper == '!=':
                    res = operator.ne(model[left].get(model),right)
                elif oper == '<':
                    res = operator.lt(model[left].get(model),right)
                elif oper == '>':
                    res = operator.gt(model[left].get(model),right)
                elif oper == '<=':
                    res = operator.le(model[left].get(model),right)
                elif oper == '>=':
                    res = operator.ge(model[left].get(model),right)
                elif oper == 'in':
                    res = operator.contains(right, model[left].get(model))
                elif oper == 'not in':
                    res = operator.contains(right, model[left].get(model))
                    res = operator.not_(res)
                return res

            #copy the list
            #eval_stack = self.cond[:]
            #eval_stack.reverse()
            res = []
            for condition in self.cond[::-1]:
                if is_operand(condition):
                    res.append(evaluate(condition))
                elif condition in ['|','&']:
                    elem_1 = res.pop()
                    elem_2 = res.pop()
                    if condition=='|':
                        res.append( any((evaluate(elem_1), evaluate(elem_2))) )
                    else:
                        res.append( all((evaluate(elem_1), evaluate(elem_2))) )
                elif condition == '!':
                    res.append(not res.pop())
            return all(res)

def call_log(fun):
    """Debug decorator
       TODO: Add optionnal execution time
    """
    def f(*args, **kwargs):
        log = logging.getLogger('call_log')
        log.info("call %s with %r, %r:" % (getattr(fun, '__name__', str(fun)), args, kwargs))
        try:
            r = fun(*args, **kwargs)
            log.info(repr(r))
            return r
        except Exception, ex:
            log.exception("Exception: %r" % (ex,))
            raise
    return f

def to_xml(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def human_size(sz):
    """
    Return the size in a human readable format
    """
    if not sz:
        return False
    units = ('bytes', 'Kb', 'Mb', 'Gb')
    s, i = float(sz), 0
    while s >= 1024 and i < len(units)-1:
        s = s / 1024
        i = i + 1
    return "%0.2f %s" % (s, units[i])

def ustr(value, from_encoding='utf-8'):
    """This method is similar to the builtin `str` method, except
    it will return Unicode string.

    @param value: the value to convert

    @rtype: unicode
    @return: unicode string
    """

    if isinstance(value, unicode):
        return value

    if hasattr(value, '__unicode__'):
        return unicode(value)

    if not isinstance(value, str):
        value = str(value)

    return unicode(value, from_encoding)

def format_connection_string(login, _passwd, server, port, protocol, dbname):
#def format_connection_string(*args):
#    login, _passwd, server, port, protocol, dbname = args
    DEFAULT_PORT = {
        'http://': 8069,
        'https://': 8069,
        'socket://': 8070,
    }
    result = '%s%s@%s' % (protocol, login, server)
    if port and DEFAULT_PORT.get(protocol) != int(port):
        result += ':%s' % (port,)
    result += '/%s' % (dbname,)
    return result

def str2bool(string, default=None):
    """Convert a string representing a boolean into the corresponding boolean

         True  | False
       --------+---------
        'True' | 'False'
        '1'    | '0'
        'on'   | 'off'
        't'    | 'f'

    If string can't be converted and default value is not None, default value
    returned, else a ValueError is raised
    """
    assert isinstance(string, basestring)
    mapping = {
        True: "true t 1 on".split(),
        False: "false f 0 off".split(),
    }
    string = string.lower()
    for value in mapping:
        if string in mapping[value]:
            return value
    if default is not None:
        return default
    raise ValueError("%r does not represent a valid boolean value" % (string,))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
