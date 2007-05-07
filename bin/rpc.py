##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import xmlrpclib
import logging
import socket

import tiny_socket

import service
import common
import options

import re

class rpc_int_exception(Exception):
	pass


class rpc_exception(Exception):
	def __init__(self, code, msg):
		log = logging.getLogger('rpc.exception')
		log.warning('CODE %s: %s' % (str(code),msg))

		self.code = code
#		lines = msg.split('\n')
		lines = code.split('\n')
		self.data = '\n'.join(lines[2:])
		self.type = lines[0].split(' -- ')[0]
		self.message = ''
		if len(lines[0].split(' -- ')) > 1:
			self.message = lines[0].split(' -- ')[1]
		

class gw_inter(object):
	__slots__ = ('_url', '_db', '_uid', '_passwd', '_sock', '_obj')
	def __init__(self, url, db, uid, passwd, obj='/object'):
		self._url = url
		self._db = db
		self._uid = uid
		self._obj = obj
		self._passwd = passwd
	def exec_auth(method, *args):
		pass
	def execute(method, *args):
		pass

class xmlrpc_gw(gw_inter):
	__slots__ = ('_url', '_db', '_uid', '_passwd', '_sock', '_obj')
	def __init__(self, url, db, uid, passwd, obj='/object'):
		gw_inter.__init__(self, url, db, uid, passwd, obj)
		self._sock = xmlrpclib.ServerProxy(url+obj)
	def exec_auth(self, method, *args):
		logging.getLogger('rpc.request').info(str((method, self._db, self._uid, self._passwd, args)))
		res = self.execute(method, self._uid, self._passwd, *args)
		logging.getLogger('rpc.result').debug(str(res))
		return res

	def __convert(self, result):
		if type(result)==type(u''):
			return result.encode('utf-8')
		elif type(result)==type([]):
			return map(self.__convert, result)
		elif type(result)==type({}):
			newres = {}
			for i in result.keys():
				newres[i] = self.__convert(result[i])
			return newres
		else:
			return result

	def execute(self, method, *args):
		result = getattr(self._sock,method)(self._db, *args)
		return self.__convert(result)

class tinySocket_gw(gw_inter):
	__slots__ = ('_url', '_db', '_uid', '_passwd', '_sock', '_obj')
	def __init__(self, url, db, uid, passwd, obj='/object'):
		gw_inter.__init__(self, url, db, uid, passwd, obj)
		self._sock = tiny_socket.mysocket()
		self._obj = obj[1:]
	def exec_auth(self, method, *args):
		logging.getLogger('rpc.request').info(str((method, self._db, self._uid, self._passwd, args)))
		res = self.execute(method, self._uid, self._passwd, *args)
		logging.getLogger('rpc.result').debug(str(res))
		return res
	def execute(self, method, *args):
		self._sock.connect(self._url)
		self._sock.mysend((self._obj, method, self._db)+args)
		res = self._sock.myreceive()
		self._sock.disconnect()
		return res

class rpc_session(object):
	__slots__ = ('_open', '_url', 'uid', 'uname', '_passwd', '_gw', 'db', 'context', 'timezone')
	def __init__(self):
		self._open = False
		self._url = None
		self._passwd = None
		self.uid = None
		self.context = {}
		self.uname = None
		self._gw = xmlrpc_gw
		self.db = None
		self.timezone = 'utc'

	def rpc_exec(self, obj, method, *args):
		try:
			sock = self._gw(self._url, self.db, self.uid, self._passwd, obj)
			return sock.execute(method, *args)
		except socket.error, (e1,e2):
			common.error(_('Connection refused !'), e1, e2)
			raise rpc_exception(69, _('Connection refused!'))
		except xmlrpclib.Fault, err:
			raise rpc_exception(err.faultCode, err.faultString)

	def rpc_exec_auth_try(self, obj, method, *args):
		if self._open:
			sock = self._gw(self._url, self.db, self.uid, self._passwd, obj)
			return sock.exec_auth(method, *args)
		else:
			raise rpc_exception(1, 'not logged')

	def rpc_exec_auth_wo(self, obj, method, *args):
		try:
			sock = self._gw(self._url, self.db, self.uid, self._passwd, obj)
			return sock.exec_auth(method, *args)
		except xmlrpclib.Fault, err:
			a = rpc_exception(err.faultCode, err.faultString)
		except tiny_socket.Myexception, err:
			a = rpc_exception(err.faultCode, err.faultString)
		if a.type in ('warning', 'UserError'):
			common.warning(a.data, a.message)
			return None
		raise a

	def rpc_exec_auth(self, obj, method, *args):
		if self._open:
			try:
				sock = self._gw(self._url, self.db, self.uid, self._passwd, obj)
				return sock.exec_auth(method, *args)
			except socket.error, (e1,e2):
				common.error(_('Connection refused !'), e1, e2)
				raise rpc_exception(69, 'Connection refused!')
			except xmlrpclib.Fault, err:
				a = rpc_exception(err.faultCode, err.faultString)
				if a.type in ('warning','UserError'):
					common.warning(a.data, a.message)
#TODO: faudrait propager l'exception
#					raise a
					pass
				else:
					pass
					common.error(_('Application Error'), err.faultCode, err.faultString)
			except tiny_socket.Myexception, err:
				a = rpc_exception(err.faultCode, err.faultString)
				if a.type in ('warning', 'UserError'):
					common.warning(a.data, a.message)
					pass
				else:
					pass
					common.error(_('Application Error'), err.faultCode, err.faultString)
			except Exception, e:
				common.error(_('Application Error'), _('View details'), str(e))
		else:
			raise rpc_exception(1, 'not logged')

	def login(self, uname, passwd, url, port, protocol, db):
		_protocol = protocol
		if _protocol == 'http://' or _protocol == 'https://':
			_url = _protocol + url+':'+str(port)+'/xmlrpc'
			_sock = xmlrpclib.ServerProxy(_url+'/common')
			self._gw = xmlrpc_gw
			try:
				res = _sock.login(db or '', uname or '', passwd or '')
			except socket.error,e:
				return -1
			if not res:
				self._open=False
				self.uid=False
				return -2
		else:
			_url = _protocol+url+':'+str(port)
			_sock = tiny_socket.mysocket()
			self._gw = tinySocket_gw
			try:
				_sock.connect(url, int(port))
				_sock.mysend(('common', 'login', db or '', uname or '', passwd or ''))
				res = _sock.myreceive()
				_sock.disconnect()
			except socket.error,e:
				return -1
			if not res:
				self._open=False
				self.uid=False
				return -2
		self._url = _url
		self._open = True
		self.uid = res
		self.uname = uname
		self._passwd = passwd
		self.db = db

		#CHECKME: is this useful? maybe it's used to see if there is no 
		# exception raised?
		sock = self._gw(self._url, self.db, self.uid, self._passwd)
		self.context_reload()
		return 1
		
	def list_db(self, url):
		m = re.match('^(http[s]?://|socket://)([\w.\-]+):(\d{1,5})$', url or '')
		if not m:
			return -1
		if m.group(1) == 'http://' or m.group(1) == 'https://':
			sock = xmlrpclib.ServerProxy(url + '/xmlrpc/db')
			try:
				return sock.list()
			except:
				return -1
		else:
			sock = tiny_socket.mysocket()
			try:
				sock.connect(m.group(2), int(m.group(3)))
				sock.mysend(('db', 'list'))
				res = sock.myreceive()
				sock.disconnect()
				return res
			except Exception, e:
				return -1
	
	def db_exec_no_except(self, url, method, *args):
		m = re.match('^(http[s]?://|socket://)([\w.\-]+):(\d{1,5})$', url or '')
		if m.group(1) == 'http://' or m.group(1) == 'https://':
			sock = xmlrpclib.ServerProxy(url + '/xmlrpc/db')
			return getattr(sock, method)(*args)
		else:
			sock = tiny_socket.mysocket()
			sock.connect(m.group(2), int(m.group(3)))
			sock.mysend(('db', method)+args)
			res = sock.myreceive()
			sock.disconnect()
			return res

	def db_exec(self, url, method, *args):
		res = False
		try:
			res = self.db_exec_no_except(url, method, *args)
		except socket.error, msg:
			common.warning('Could not contact server!')
		return res

	def context_reload(self):
		self.context = {}
		self.timezone = 'utc'
		# self.uid
		context = self.rpc_exec_auth('/object', 'execute', 'ir.values', 'get', 'meta', False, [('res.users', self.uid or False)], False, {}, True, True, False)
		for c in context:
			if c[2]:
				self.context[c[1]] = c[2]
			if c[1] == 'lang':
				ids = self.rpc_exec_auth('/object', 'execute', 'res.lang', 'search', [('code', '=', c[2])])
				if ids:
					l = self.rpc_exec_auth('/object', 'execute', 'res.lang', 'read', ids, ['direction'])
					if l and 'direction' in l[0]:
						common.DIRECTION = l[0]['direction']
						import gtk
						if common.DIRECTION == 'rtl':
							gtk.widget_set_default_direction(gtk.TEXT_DIR_RTL)
						else:
							gtk.widget_set_default_direction(gtk.TEXT_DIR_LTR)
			elif c[1] == 'tz':
				self.timezone = self.rpc_exec_auth('/common', 'timezone_get')
				try:
					import pytz
				except:
					common.warning('You select a timezone but tinyERP could not find pytz library !\nThe timezone functionality will be disable.')

	def logged(self):
		return self._open

	def logout(self):
		if self._open:
			self._open = False
			self.uname = None
			self.uid = None
			self._passwd = None
		else:
			pass

session = rpc_session()


class RPCProxy(object):

	def __init__(self, resource):
		self.resource = resource
		self.__attrs = {}

	def __getattr__(self, name):
		if not name in self.__attrs:
			self.__attrs[name] = RPCFunction(self.resource, name)
		return self.__attrs[name]
	

class RPCFunction(object):

	def __init__(self, object, func_name):
		self.object = object
		self.func = func_name

	def __call__(self, *args):
		return session.rpc_exec_auth('/object', 'execute', self.object, self.func, *args)
