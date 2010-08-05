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

import socket
import cPickle
import sys
import options
import gzip
import StringIO

DNS_CACHE = {}

# disable Nagle problem.
# -> http://www.cmlenz.net/archives/2008/03/python-httplib-performance-problems
class NoNagleSocket(socket.socket):
    def __init__(self, *args, **kwargs):
        super(NoNagleSocket, self).__init__(*args, **kwargs)
        self.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

socket.socket = NoNagleSocket


class Myexception(Exception):
    def __init__(self, faultCode, faultString):
        self.faultCode = faultCode
        self.faultString = faultString
        self.args = (faultCode, faultString)

class mysocket:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.sock.settimeout(int(options.options['client.timeout']))

    def connect(self, host, port=False):
        if not port:
            protocol, buf = host.split('//')
            host, port = buf.split(':')
        if host in DNS_CACHE:
            host = DNS_CACHE[host]
        self.sock.connect((host, int(port)))
        DNS_CACHE[host], port = self.sock.getpeername()

    def disconnect(self):
        # on Mac, the connection is automatically shutdown when the server disconnect.
        # see http://bugs.python.org/issue4397
        if sys.platform != 'darwin':
            self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def mysend(self, msg, exception=False, traceback=None):
        msg = cPickle.dumps([msg,traceback])
        self.sock.sendall('%8d%s%s' % (len(msg), exception and "1" or "0", msg))

    def myreceive(self):
        def read(socket, size):
            buf=''
            while len(buf) < size:
                chunk = self.sock.recv(size - len(buf))
                if chunk == '':
                    raise RuntimeError, "socket connection broken"
                buf += chunk
            return buf

        size = int(read(self.sock, 8))
        buf = read(self.sock, 1)
        exception = buf != '0' and buf or False
        res = cPickle.loads(read(self.sock, size))

        if isinstance(res[0],Exception):
            if exception:
                if not isinstance(res[1],basestring):
                        str1=str(res[1])
                else:
                        str1=res[1]
                raise Myexception(str(res[0]), str1)
            raise res[0]
        else:
            return res[0]

from xmlrpclib import Transport,ProtocolError

import httplib
class HTTP11(httplib.HTTP):
        _http_vsn = 11
        _http_vsn_str = 'HTTP/1.1'
        
        def is_idle(self):
            return self._conn and self._conn._HTTPConnection__state == httplib._CS_IDLE
        
try:
        if sys.version_info[0:2] < (2,6):
            # print "No https for python %d.%d" % sys.version_info[0:2]
            raise AttributeError()

        class HTTPS(httplib.HTTPS):
            _http_vsn = 11
            _http_vsn_str = 'HTTP/1.1'
                
            def is_idle(self):
                return self._conn and self._conn._HTTPConnection__state == httplib._CS_IDLE
                # Still, we have a problem here, because we cannot tell if the connection is
                # closed.

except AttributeError:
    # if not in httplib, define a class that will always fail.
    class HTTPS():
        def __init__(self,*args):
            raise NotImplementedError( "your version of httplib doesn't support HTTPS" )
        


class PersistentTransport(Transport):
    """Handles an HTTP transaction to an XML-RPC server, persistently."""

    def __init__(self, use_datetime=0, send_gzip=False):
        self._use_datetime = use_datetime
        self._http = {}
        self._send_gzip = send_gzip
        # print "Using persistent transport"

    def make_connection(self, host):
        # create a HTTP connection object from a host descriptor
        if not self._http.has_key(host):
            host, extra_headers, x509 = self.get_host_info(host)
            self._http[host] = HTTP11(host)
            # print "New connection to",host
        if not self._http[host].is_idle():
            # Here, we need to discard a busy or broken connection.
            # It might be the case that another thread is using that
            # connection, so it makes more sense to let the garbage
            # collector clear it.
            self._http[host] = None
            host, extra_headers, x509 = self.get_host_info(host)
            self._http[host] = HTTP11(host)
            # print "New connection to",host
        
        return self._http[host]

    def get_host_info(self, host):
        host, extra_headers, x509 = Transport.get_host_info(self,host)
        if extra_headers == None:
            extra_headers = []
                
        extra_headers.append( ( 'Connection', 'keep-alive' ))
        
        return host, extra_headers, x509

    def _parse_response(self, response):
        """ read response from input file/socket, and parse it
            We are persistent, so it is important to only parse
            the right amount of input
        """

        p, u = self.getparser()

        if response.msg.get('content-encoding') == 'gzip':
            gzdata = StringIO.StringIO()
            while not response.isclosed():
                rdata = response.read(1024)
                if not rdata:
                    break
                gzdata.write(rdata)
            gzdata.seek(0)
            rbuffer = gzip.GzipFile(mode='rb', fileobj=gzdata)
            while True:
                respdata = rbuffer.read()
                if not respdata:
                    break
                p.feed(respdata)
        else:
            while not response.isclosed():
                rdata = response.read(1024)
                if not rdata:
                    break
                if self.verbose:
                    print "body:", repr(response)
                p.feed(rdata)
                if len(rdata)<1024:
                    break

        p.close()
        return u.close()

    def request(self, host, handler, request_body, verbose=0):
        # issue XML-RPC request

        try:
            h = self.make_connection(host)
            if verbose:
                h.set_debuglevel(1)

            self.send_request(h, handler, request_body)
        except httplib.CannotSendRequest:
            # try once more..
            if h: h.close()
            h = self.make_connection(host)
            if verbose:
                h.set_debuglevel(1)

            self.send_request(h, handler, request_body)

        self.send_host(h, host)
        self.send_user_agent(h)
        self.send_content(h, request_body)

        resp = None
        try:
            resp = h._conn.getresponse()
            # TODO: except BadStatusLine, e:
                
            errcode, errmsg, headers = resp.status, resp.reason, resp.msg
            if errcode != 200:
                raise ProtocolError( host + handler, errcode, errmsg, headers )

            self.verbose = verbose

            try:
                sock = h._conn.sock
            except AttributeError:
                sock = None

            return self._parse_response(resp)
        finally:
            if resp: resp.close()

    def send_content(self, connection, request_body):
        connection.putheader("Content-Type", "text/xml")
        
        if self._send_gzip and len(request_body) > 512:
            buffer = StringIO.StringIO()
            output = gzip.GzipFile(mode='wb', fileobj=buffer)
            output.write(request_body)
            output.close()
            buffer.seek(0)
            request_body = buffer.getvalue()
            connection.putheader('Content-Encoding', 'gzip')

        connection.putheader("Content-Length", str(len(request_body)))
        connection.putheader("Accept-Encoding",'gzip')
        connection.endheaders()
        if request_body:
            connection.send(request_body)

    def send_request(self, connection, handler, request_body):
        connection.putrequest("POST", handler, skip_accept_encoding=1)


class SafePersistentTransport(PersistentTransport):
    """Handles an HTTPS transaction to an XML-RPC server."""

    # FIXME: mostly untested

    def make_connection(self, host):
        # create a HTTPS connection object from a host descriptor
        # host may be a string, or a (host, x509-dict) tuple
        if not self._http.has_key(host):
            import httplib
            host, extra_headers, x509 = self.get_host_info(host)
            self._http[host] = HTTPS(host, None, **(x509 or {}))
        return self._http[host]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

