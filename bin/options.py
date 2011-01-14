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

import ConfigParser,optparse
import os, sys
import gtk
import gettext

def get_home_dir():
    """Return the closest possible equivalent to a 'home' directory.
    For Posix systems, this is $HOME, and on NT it's $HOMEDRIVE\$HOMEPATH.
    Currently only Posix and NT are implemented, a HomeDirError exception is
    raised for all other OSes. """

    if os.name == 'posix':
        return os.path.expanduser('~')
    elif os.name == 'nt':
        try:
            return os.path.join(os.environ['HOMEDRIVE'],os.environ['HOMEPATH'])
        except:
            try:
                import _winreg as wreg
                key = wreg.OpenKey(wreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
                homedir = wreg.QueryValueEx(key,'Personal')[0]
                key.Close()
                return homedir
            except:
                return 'C:\\'
    elif os.name == 'dos':
        return 'C:\\'
    else:
        return '.'

class configmanager(object):
    def __init__(self,fname=None):
        self.options = {
            'login.login': 'demo',
            'login.server': 'localhost',
            'login.port': '8070',
            'login.protocol': 'socket://',
            'login.db': 'terp',
            'client.toolbar': 'both',
            'client.theme': 'none',
            'path.share': os.path.join(sys.prefix, 'share/openerp-client/'),
            'path.pixmaps': os.path.join(sys.prefix, 'share/pixmaps/openerp-client/'),
            'tip.autostart': False,
            'tip.position': 0,
            'survey.position': 0,
            'form.autosave': False,
            'printer.preview': True,
            'printer.softpath': 'none',
            'printer.softpath_html': 'none',
            'printer.path': 'none',
            'logging.logger': '',
            'logging.level': 'DEBUG',
            'logging.output': 'stdout',
            'logging.verbose': False,
            'client.default_path': os.path.expanduser('~'),
            'support.recipient': 'support@openerp.com',
            'support.support_id' : '',
            'form.toolbar': True,
            'client.form_tab': 'top',
            'client.form_tab_orientation': 0,
            'client.lang': False,
            'client.filetype': {},
            'help.index': 'http://www.openerp.com/documentation/user-manual/',
            'help.context': 'http://www.openerp.com/scripts/context_index.php'
        }
        parser = optparse.OptionParser(version=_("OpenERP Client %s" % openerp_version))
        parser.add_option("-c", "--config", dest="config",help=_("specify alternate config file"))
        parser.add_option("-v", "--verbose", action="store_true", default=False, dest="verbose", help=_("enable basic debugging"))
        parser.add_option("-d", "--log", dest="log_logger", default='', help=_("specify channels to log"))
        parser.add_option("-l", "--log-level", dest="log_level",default='ERROR', help=_("specify the log level: INFO, DEBUG, WARNING, ERROR, CRITICAL"))
        parser.add_option("-u", "--user", dest="login", help=_("specify the user login"))
        parser.add_option("-p", "--port", dest="port", help=_("specify the server port"))
        parser.add_option("-s", "--server", dest="server", help=_("specify the server ip/name"))
        (opt, args) = parser.parse_args()

        self.rcfile = self._get_rcfile(fname, opt.config)
        self.load()

        if opt.verbose:
            self.options['logging.verbose']=True
        self.options['logging.logger'] = opt.log_logger
        self.options['logging.level'] = opt.log_level

        for arg in ('login', 'port', 'server'):
            if getattr(opt, arg):
                self.options['login.'+arg] = getattr(opt, arg)

    def _get_rcfile(self, fname, optconfigfile):
        rcfile = fname or optconfigfile or os.environ.get('OPENERPRC') or os.path.join(get_home_dir(), '.openerprc')
        if not os.path.exists(rcfile):
            import logging
            log = logging.getLogger('common.options')
            additional_info = ""
            if optconfigfile:
                additional_info = " Be sure to specify an absolute path name if you are using the '-c' command line switch"
            log.warn('Config file %s does not exist !%s'% (rcfile, additional_info ))
        return os.path.abspath(rcfile)

    def save(self, fname = None):
        try:
            p = ConfigParser.ConfigParser()
            sections = {}
            for o in self.options.keys():
                if not len(o.split('.'))==2:
                    continue
                osection,oname = o.split('.')
                if not p.has_section(osection):
                    p.add_section(osection)
                p.set(osection,oname,self.options[o])
            p.write(file(self.rcfile,'wb'))
        except:
            import logging
            log = logging.getLogger('common.options')
            log.warn('Unable to write config file %s !'% (self.rcfile,))
        return True


    def load(self, fname=None):
        try:
            self.rcexist = False
            if not os.path.isfile(self.rcfile):
                self.save()
                return False
            self.rcexist = True

            p = ConfigParser.ConfigParser()
            p.read([self.rcfile])
            for section in p.sections():
                for (name,value) in p.items(section):
                    if value=='True' or value=='true':
                        value = True
                    if value=='False' or value=='false':
                        value = False
                    self.options[section+'.'+name] = value
        except Exception, e:
            import logging
            log = logging.getLogger('common.options')
            log.warn('Unable to read config file %s !'% (self.rcfile,))
        return True

    def __setitem__(self, key, value):
        self.options[key]=value

    def __getitem__(self, key):
        return self.options[key]

options = configmanager()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

