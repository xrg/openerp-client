# -*- coding: utf-8 -*-
##############################################################################
#
#   This following code is based on the gnome-distutils module that is
#   part of Gnomolicious, from http://www.nongnu.org/gnomolicious/
#   The original licensing terms and copyright are included below.
#
#   Subsequent modifications to the original code were done by OpenERP S.A,
#   and distributed under the GNU AGPL. These licensing terms are also
#   included below.
#
# ---------------- OpenERP Licensing Terms ---------------------------------
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 OpenERP S.A. (<http://openerp.com>).
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
# ---------------- Original Gnomolicious Licensing terms --------------------
#
#   Gnomolicious is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   Gnomolicious is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Gnomolicious; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#   (C) 2003, 2005 Terje Rosten <terjeros@phys.ntnu.no>, Nicolas Evrard
#
##############################################################################


import sys
import os
import os.path
import msgfmt

from setuptools import Command, Distribution
from distutils.command.build_scripts import build_scripts
from setuptools.command.install import install
from distutils.command.install_data import install_data
from distutils.dep_util import newer
import distutils.core

from distutils.errors import DistutilsSetupError

try:
    from dsextras import BuildExt
    _pyflakes_hush = [ BuildExt, ]
except ImportError:
    try:
        from gtk.dsextras import BuildExt
        _pyflakes_hush = [ BuildExt, ]
    except ImportError:
        sys.exit('Error: Can not find dsextras or gtk.dsextras')

# get python short version
py_short_version = '%s.%s' % sys.version_info[:2]

class build_scripts_app(build_scripts):
    """ Create the shortcut to the application
    """

    description = 'build the OpenERP Client Linux script'

    def get_source_files(self):
        return [ x for x in self.scripts if x != 'openerp-client']

    def run(self):
        if sys.platform != 'win32':
            self.announce("create startup script")
            opj = os.path.join
            # Peek into "install" command to find out where it is going to install to
            inst_cmd = self.get_finalized_command('install')
            if inst_cmd:
                # Note: we user the "purelib" because we don't ship binary
                # executables. If we ever compile things into execs, we shall 
                # use "platlib"
                openerp_site_packages = opj(inst_cmd.install_purelib,'openerp-client')
                if inst_cmd.root and openerp_site_packages.startswith(inst_cmd.root):
                    # trick: when we install relative to root, we mostly mean to
                    # temporary put the files there, and then move back to the
                    # stripped prefix dir. So we don't write the full root into
                    # the script
                    iroot = inst_cmd.root
                    if iroot.endswith('/'):
                        iroot = iroot[:-1]
                    openerp_site_packages = openerp_site_packages[len(iroot):]
           
            else:
                # Hard-code the Linux /usr/lib/pythonX.Y/... path
                openerp_site_packages = opj('/usr', 'lib', 'python%s' % py_short_version, 'site-packages', 'openerp-client')
            start_script = "#!/bin/sh\ncd %s\nexec %s ./openerp-client.py $@\n" % (openerp_site_packages, sys.executable)
            # write script
            f = open('openerp-client', 'w')
            f.write(start_script)
            f.close()
        build_scripts.run(self)

class build_mo(Command):

    description = 'build binary message catalog'

    user_options = [
        ('build-base=', 'b', 'directory to build to')]

    def initialize_options(self):
        self.build_base = None
        self.translations = self.distribution.translations
        self.force = None

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_base', 'build_base'),
                                   ('force', 'force'))
    def run(self):
        if not self.translations:
            return
        self.announce('Building binary message catalog')
        for mo, po in self.translations:
            dest = os.path.normpath( os.path.join(self.build_base, mo))
            self.mkpath(os.path.dirname(dest))
            if not self.force and not newer(po, dest):
                self.announce("not building %s (up-to-date)" % dest)
            else:
                msgfmt.make(po, dest)

class install_mo(install_data):

    description = 'install generated binary message catalog'

    def initialize_options(self):
        install_data.initialize_options(self)
        self.translations = self.distribution.translations
        self.install_dir = None
        self.build_dir = None
        self.skip_build = None
        self.outfiles = []
        
    def finalize_options(self):
        install_data.finalize_options(self)
        self.set_undefined_options('build_mo', ('build_base', 'build_dir'))
        self.set_undefined_options('install',
                                   ('install_data', 'install_dir'),
                                   ('skip_build', 'skip_build'))
    def run(self):
        if not self.skip_build:
            self.run_command('build_mo')
        if self.translations:
            for mo, po in self.translations:
                src = os.path.normpath(self.build_dir + '/' + mo)
                if not os.path.isabs(mo):
                    dest =  os.path.normpath(self.install_dir + '/' + mo)
                elif self.root:
                    dest = self.root + mo
                else:
                    dest = mo
                self.mkpath(os.path.dirname(dest))
                (out, _) = self.copy_file(src, dest)
                self.outfiles.append(out)

    def get_outputs (self):
        return self.outfiles

    def get_inputs (self):
        return [ po for mo, po in self.translations ]

class ClientDistribution(Distribution):
    def __init__(self, attrs=None):
        self.translations = []
        Distribution.__init__(self, attrs)
        self.cmdclass = {
            'install_mo' : install_mo,
            'build_mo' : build_mo,
            # 'build_conf' : build_conf,
            'build_ext': BuildExt,
            'build_scripts': build_scripts_app,
            }
        self.command_obj['build_scripts'] = None


#eof
