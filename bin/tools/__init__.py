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


def expr_eval(string, context={}):
    import rpc
    context['uid'] = rpc.session.uid
    if isinstance(string, basestring):
        return eval(string, context)
    else:
        return string

def launch_browser(url):
    import webbrowser
    import sys
    if sys.platform == 'win32':
        webbrowser.open(url)
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
    result = {}
    attrs = node.attributes
    if attrs is None:
        return {}
    for i in range(attrs.length):
        result[attrs.item(i).localName] = str(attrs.item(i).nodeValue)
        if attrs.item(i).localName == "digits" and isinstance(attrs.item(i).nodeValue, (str, unicode)):
            result[attrs.item(i).localName] = eval(attrs.item(i).nodeValue)
    return result

#FIXME use spaces
def calc_condition(self,model,con):
	if model and (con[0] in model.mgroup.fields):
		val = model[con[0]].get(model)
		if con[1]=="=":
			if val==con[2]:
				return True
		elif con[1]=="!=":
			if val!=con[2]:
				return True
		elif con[1]=="<":
			if val<con[2]:
				return True
		elif con[1]==">":
			if val>con[2]:
				return True
		elif con[1]=="<=":
			if val<=con[2]:
				return True
		elif con[1]==">=":
			if val>=con[2]:
				return True
		return False

def call_log(fun):
    """Debug decorator
       TODO: Add optionnal execution time
    """
    def f(*args, **kwargs):
        print "call %s with %r, %r:" % (getattr(fun, '__name__', str(fun)), args, kwargs),
        try:
            r = fun(*args, **kwargs)
            print repr(r)
            return r
        except Exception, ex:
            print "Exception: %r" % (ex,)
            raise
    return f

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
