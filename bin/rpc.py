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

import gtk
import xmlrpclib
import logging
import socket

import tiny_socket
import service
import common
import options
import os
import urllib

import re

CONCURRENCY_CHECK_FIELD = '__last_update'

session_counter = 0

class rpc_exception(Exception):
    def __init__(self, code, backtrace):

        self.code = code
        self.args = backtrace
        if hasattr(code, 'split'):
            lines = code.split('\n')

            self.type = lines[0].split(' -- ')[0]
            message = ''
            if len(lines[0].split(' -- ')) > 1:
                message = lines[0].split(' -- ')[1]

            self.args = (message, '\n'.join(lines[2:]))
        else:
            self.type = 'error'
            self.args = (backtrace,)

        self.backtrace = backtrace

        log = logging.getLogger('rpc.exception')
        log.warning('CODE %s: %s' % (str(code), self.args[0]))

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
        ttype, someuri = urllib.splittype(url)
        if ttype not in ("http", "https"):
            raise IOError, "unsupported XML-RPC protocol"
        if ttype == "https":
            transport = tiny_socket.SafePersistentTransport()
        else:
            transport = tiny_socket.PersistentTransport()
        self._sock = xmlrpclib.ServerProxy(url+obj, transport=transport, verbose=0)
    def exec_auth(self, method, *args):
        logging.getLogger('rpc.request').debug_rpc(str((method, self._db, self._uid, self._passwd, args)))
        res = self.execute(method, self._uid, self._passwd, *args)
        logging.getLogger('rpc.result').debug_rpc_answer(str(res))
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
        # If a socket error occurs here, we will let it propagate.
        # it is safer than trying an operation twice (it may perform double
        # actions, which mess with the data).
        result = getattr(self._sock,method)(self._db, *args)
        return self.__convert(result)

    def login(self):
        return self._sock.login(self._db, self._uid, self._passwd)

class tinySocket_gw(gw_inter):
    __slots__ = ('_url', '_db', '_uid', '_passwd', '_sock', '_obj')
    def __init__(self, url, db, uid, passwd, obj='/object'):
        gw_inter.__init__(self, url, db, uid, passwd, obj)
        self._obj = obj[1:]
    def __del__(self):
        pass
    def exec_auth(self, method, *args):
        logging.getLogger('rpc.request').debug_rpc(str((method, self._db, self._uid, self._passwd, args)))
        res = self.execute(method, self._uid, self._passwd, *args)
        logging.getLogger('rpc.result').debug_rpc_answer(str(res))
        return res
    def execute(self, method, *args):
        # We are not yet ready for persistent connections, so open and close
        # the connectionn at each call.
        self._sock = tiny_socket.mysocket()
        self._sock.connect(self._url)
        self._sock.mysend((self._obj, method, self._db)+args)
        res = self._sock.myreceive()
        self._sock.disconnect()
        return res

class rpc_session(object):
    __slots__ = ('_open', '_url', 'uid', 'uname', '_passwd', '_ogws', 'db', 'context', 'timezone', 'rpcproto', 'server_version')
    def __init__(self):
        self._open = False
        self._url = None
        self._passwd = None
        self.uid = None
        self.context = {}
        self.uname = None
        self._ogws = {}
        self.db = None
        self.rpcproto = None
        self.timezone = 'utc'

    def rpc_exec(self, obj, method, *args):
        try:
            #sock = self._gw(self._url, self.db, self.uid, self._passwd, obj)
            return self.gw(obj).execute(method, *args)
        except socket.error, e:
            common.message(str(e), title=_('Connection refused !'), type=gtk.MESSAGE_ERROR)
            raise rpc_exception(69, _('Connection refused!'))
        except xmlrpclib.Fault, err:
            raise rpc_exception(err.faultCode, err.faultString or str(err))

    def rpc_exec_auth_try(self, obj, method, *args):
        if self._open:
            #sock = self._gw(self._url, self.db, self.uid, self._passwd, obj)
            return self.gw(obj).exec_auth(method, *args)
        else:
            raise rpc_exception(1, 'not logged')

    def rpc_exec_auth_wo(self, obj, method, *args):
        try:
            #sock = self._gw(self._url, self.db, self.uid, self._passwd, obj)
            return self_gw(obj).exec_auth(method, *args)
        except xmlrpclib.Fault, err:
            a = rpc_exception(err.faultCode, err.faultString)
        except tiny_socket.Myexception, err:
            a = rpc_exception(err.faultCode, err.faultString)
            if a.code in ('warning', 'UserError'):
                common.warning(a.args[1], a.args[0])
            return None
        raise a

    def rpc_exec_auth(self, obj, method, *args):
        if self._open:
            try:
                return self.gw(obj).exec_auth(method, *args)
            except socket.error, e:
                import traceback, sys
                if hasattr(e, 'traceback'):
                        tb = e.traceback
                else:
                        tb = sys.exc_info()
                tb_s = "".join(traceback.format_exception(*tb))
                print 'socket error:',e, "\n", tb_s
                common.message(_('Unable to reach to OpenERP server !\nYou should check your connection to the network and the OpenERP server.'), _('Connection Error'), type=gtk.MESSAGE_ERROR)
                raise rpc_exception(69, 'Connection refused!')
            except Exception, e:
                if isinstance(e, xmlrpclib.Fault) \
                        or isinstance(e, tiny_socket.Myexception):
                    a = rpc_exception(e.faultCode, e.faultString)
                    if a.type in ('warning','UserError'):
                        if a.args[0] in ('ConcurrencyException') and len(args) > 4:
                            if common.concurrency(args[0], args[2][0], args[4]):
                                if CONCURRENCY_CHECK_FIELD in args[4]:
                                    del args[4][CONCURRENCY_CHECK_FIELD]
                                return self.rpc_exec_auth(obj, method, *args)
                        else:
                            common.warning(a.args[1], a.args[0])
                    else:
                        common.error(_('Application Error'), e.faultCode, e.faultString)
                else:
                    common.error(_('Application Error'), _('View details'), str(e) or str(type(e)))
                #TODO Must propagate the exception?
                raise
        else:
            raise rpc_exception(1, 'not logged')

    def gw(self,obj):
        """ Return the persistent gateway for some object
        """
        global session_counter
        if not self._ogws.has_key(obj):
                if (self.rpcproto == 'xmlrpc'):
                        self._ogws[obj] = xmlrpc_gw(self._url, self.db, self.uid, self._passwd, obj = obj)
                elif self.rpcproto == 'netrpc':
                        self._ogws[obj] = tinySocket_gw(self._url, self.db, self.uid, self._passwd, obj = obj)
                else:
                        raise Exception("Unknown proto: %s" % self.rpcproto)
                
                session_counter = session_counter + 1
                if (session_counter % 100) == 0:
                        print "Sessions:", session_counter
        
        return self._ogws[obj]

    def login(self, uname, passwd, url, port, protocol, db):
        _protocol = protocol
        if _protocol == 'http://' or _protocol == 'https://':
            self.rpcproto = 'xmlrpc'
            _url = _protocol + url+':'+str(port)+'/xmlrpc'
            _sock = xmlrpclib.ServerProxy(_url+'/common')
            try:
                res = _sock.login(db or '', uname or '', passwd or '')
            except socket.error,e:
                common.error(_('Login error:'), str(e))
                return -1
            except:
                import sys
                common.error(_('Login error:'),str(sys.exc_info()))
                return 0
            if not res:
                self._open=False
                self.uid=False
                return -2
        else: #maybe elif ..
            _url = _protocol+url+':'+str(port)
            _sock = tiny_socket.mysocket()
            self.rpcproto = "netrpc"
            try:
                _sock.connect(url, int(port))
                _sock.mysend(('common', 'login', db or '', uname or '', passwd or ''))
                res = _sock.myreceive()
                _sock.disconnect()
            except socket.error,e:
                common.error(_('Login error:'), str(e))
                return -1
            except Exception:
                return 0
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

        self.context_reload()
        return 1

    def migrate_databases(self, url, password, databases):
        return self.exec_no_except(url, 'db', 'migrate_databases', password, databases)

    def get_available_updates(self, url, password, contract_id, contract_password):
        return self.exec_no_except(url, 'common', 'get_available_updates', password, contract_id, contract_password)

    def get_migration_scripts(self, url, password, contract_id, contract_password):
        return self.exec_no_except(url, 'common', 'get_migration_scripts', password, contract_id, contract_password)

    def about(self, url):
        return self.exec_no_except(url, 'common', 'about')

    def login_message(self, url):
        try:
            return self.exec_no_except(url, 'common', 'login_message')
        except:
            return False

    def list_db(self, url):
        try:
            return self.db_exec_no_except(url, 'list')
        except (xmlrpclib.Fault, tiny_socket.Myexception), e:
            if e.faultCode == 'AccessDenied':
                return None
            raise
        except socket.error, err:
            import locale
            language, in_encoding = locale.getdefaultlocale()
            common.warning(err[1].decode(in_encoding),_('Socket error'))
            return -1
        except RuntimeError, err:
                import locale
                language, in_encoding = locale.getdefaultlocale()
                try:
                        err_string = err[1].decode(in_encoding)
                except:
                        err_string = str(err)
                common.warning(err_string,_('Cannot list db:'))
                return -1

    def db_exec_no_except(self, url, method, *args):
        return self.exec_no_except(url, 'db', method, *args)

    def exec_no_except(self, url, resource, method, *args):
        m = re.match('^(http[s]?://|socket://)([\w.\-]+):(\d{1,5})$', url or '')
        if m.group(1) == 'http://' or m.group(1) == 'https://':
            sock = xmlrpclib.ServerProxy(url + '/xmlrpc/' + resource)
            return getattr(sock, method)(*args)
        else:
            sock = tiny_socket.mysocket()
            sock.connect(m.group(2), int(m.group(3)))
            sock.mysend((resource, method)+args)
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
        self.context = self.rpc_exec_auth('/object', 'execute', 'res.users', 'context_get') or {}
        if 'lang' in self.context:
            import translate
            translate.setlang(self.context['lang'])
            options.options['client.lang']=self.context['lang']
            ids = self.rpc_exec_auth('/object', 'execute', 'res.lang', 'search', [('code', '=', self.context['lang'])])
            if ids:
                l = self.rpc_exec_auth('/object', 'execute', 'res.lang', 'read', ids, ['direction'])
                if l and 'direction' in l[0]:
                    common.DIRECTION = l[0]['direction']
                    import gtk
                    if common.DIRECTION == 'rtl':
                        gtk.widget_set_default_direction(gtk.TEXT_DIR_RTL)
                    else:
                        gtk.widget_set_default_direction(gtk.TEXT_DIR_LTR)
        if self.context.get('tz'):
            # FIXME: Timezone handling
            #   rpc_session.timezone contains the server's idea of its timezone (from time.tzname[0]),
            #   which is quite quite unreliable in some cases. We'll fix this in trunk.
            self.timezone = self.rpc_exec_auth('/common', 'timezone_get')
            try:
                import pytz
                pytz.timezone(self.timezone)
            except pytz.UnknownTimeZoneError:
                # Server timezone is not recognized!
                # Time values will be displayed as if located in the server timezone. (nothing we can do)
                pass
        try:
            url = self._url
            if url.endswith('/xmlrpc'):
                url = url[:-7]
            sv = self.db_exec_no_except(url, 'server_version')
            if sv.endswith('dev'):
                sv = sv[:-3]
            self.server_version = map(int, sv.split('.'))
            print "Connected to a server ver: %s" % (self.server_version)
        except Exception, e:
            import traceback
            traceback.print_exc()
            common.warning(_("Could not get server's version: %s") % e)

    def logged(self):
        return self._open

    def logout(self):
        if self._open:
            self._open = False
            self.uname = None
            self._ogws = {}
            self.uid = None
            self._passwd = None

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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

