#!/usr/bin/env python
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

# setup for OpenERP GTK client
#   taken from straw http://www.nongnu.org/straw/index.html
#   taken from gnomolicious http://www.nongnu.org/gnomolicious/
#   adapted by Nicolas Évrard <nicoe@altern.org>

import sys
import os
import glob

from setuptools import setup
from setuptools.command.install import install as suc_install
from distutils.sysconfig import get_python_lib
from mydistutils import ClientDistribution

has_py2exe = False
if sys.platform == 'win32':
    import py2exe
    has_py2exe = True

    origIsSystemDLL = py2exe.build_exe.isSystemDLL
    def isSystemDLL(pathname):
        if os.path.basename(pathname).lower() in ("msvcp71.dll", "mfc71.dll"):
                return 0
        return origIsSystemDLL(pathname)
    py2exe.build_exe.isSystemDLL = isSystemDLL

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bin"))

opj = os.path.join

execfile(opj('bin', 'release.py'))

if len(sys.argv) > 1 and sys.argv[1] == 'bdist_rpm':
    version = version.split('-')[0]

# get python short version
py_short_version = '%s.%s' % sys.version_info[:2]

def data_files():
    '''Build list of data files to be installed'''
    files = []
    if sys.platform == 'win32':
        import matplotlib
        datafiles = matplotlib.get_py2exe_datafiles()
        if isinstance(datafiles, list):
            files.extend(datafiles)
        else:
            files.append(datafiles)
        os.chdir('bin')
        for (dp, dn, names) in os.walk('share\\locale'):
            files.append((dp, map(lambda x: opj('bin', dp, x), names)))
        os.chdir('..')
        files.append((".",["bin\\openerp.glade", "bin\\win_error.glade", 'bin\\tipoftheday.txt', 'doc\\README.txt']))
        files.append(("pixmaps", glob.glob("bin\\pixmaps\\*.*")))
        files.append(("po", glob.glob("bin\\po\\*.*")))
        files.append(("icons", glob.glob("bin\\icons\\*.png")))
        files.append(("share\\locale", glob.glob("bin\\share\\locale\\*.*")))
    else:
        files.append((opj('share','man','man1',''),['man/openerp-client.1']))
        files.append((opj('share','doc', 'openerp-client-%s' % version), [f for
            f in glob.glob('doc/*') if os.path.isfile(f)]))
        files.append((opj('share', 'pixmaps', 'openerp-client'),
            glob.glob('bin/pixmaps/*.png')))
        files.append((opj('share', 'pixmaps', 'openerp-client', 'icons'),
            glob.glob('bin/icons/*.png')))
        files.append((opj('share', 'openerp-client'), ['bin/openerp.glade', 'bin/tipoftheday.txt',
                                                       'bin/win_error.glade']))
    return files

included_plugins = ['workflow_print']

def find_plugins():
    for plugin in included_plugins:
        path=opj('bin', 'plugins', plugin)
        for dirpath, dirnames, filenames in os.walk(path):
            if '__init__.py' in filenames:
                modname = dirpath.replace(os.path.sep, '.')
                yield modname.replace('bin', 'openerp-client', 1)

def translations():
    trans = []
    dest = 'share/locale/%s/LC_MESSAGES/%s.mo'
    for po in glob.glob('bin/po/*.po'):
        lang = os.path.splitext(os.path.basename(po))[0]
        trans.append((dest % (lang, name), po))
    return trans

if sys.platform != 'win32' and 'build_po' in sys.argv:
    os.system('(cd bin ; find . -name \*.py && find . -name \*.glade | xargs xgettext -o po/%s.pot)' % name)
    for file in ([ os.path.join('bin', 'po', fname) for fname in os.listdir('bin/po') ]):
        if os.path.isfile(file):
            os.system('msgmerge --update --backup=off %s bin/po/%s.pot' % (file, name))
    sys.exit()

options = {
    "py2exe": {
        "compressed": 1,
        "optimize": 1,
        "dist_dir": 'dist',
        "packages": [
            "encodings","gtk", "matplotlib", "pytz", "OpenSSL",
            "lxml", "lxml.builder", "lxml._elementpath", "lxml.etree",
            "lxml.objectify", "decimal"
        ],
        "includes": "pango,atk,gobject,cairo,atk,pangocairo,matplotlib._path",
        "excludes": ["Tkinter", "tcl", "TKconstants"],
        "dll_excludes": [
            "iconv.dll","intl.dll","libatk-1.0-0.dll",
            "libgdk_pixbuf-2.0-0.dll","libgdk-win32-2.0-0.dll",
            "libglib-2.0-0.dll","libgmodule-2.0-0.dll",
            "libgobject-2.0-0.dll","libgthread-2.0-0.dll",
            "libgtk-win32-2.0-0.dll","libpango-1.0-0.dll",
            "libpangowin32-1.0-0.dll",
            "wxmsw26uh_vc.dll",
        ],
    }
}

complementary_arguments = dict()

if sys.platform == 'win32':
    complementary_arguments['windows'] = [
        {
            'script' : os.path.join('bin', 'openerp-client.py'),
            'icon_resources' : [(1, os.path.join('bin', 'pixmaps', 'openerp-icon.ico'))],
            'install_requires': [ 'PyGTK', ],
        }
    ]
else:
    complementary_arguments['scripts'] = ['openerp-client']
    complementary_arguments['distclass'] = ClientDistribution


suc_install.sub_commands.append(('install_mo',  None))

setup(name             = name,
      version          = version,
      description      = description,
      long_description = long_desc,
      url              = url,
      author           = author,
      author_email     = author_email,
      classifiers      = filter(None, classifiers.splitlines()),
      license          = license,
      data_files       = data_files(),
      translations     = translations(),
      packages         = ['openerp-client',
                          'openerp-client.common',
                          'openerp-client.modules',
                          'openerp-client.modules.action',
                          'openerp-client.modules.gui',
                          'openerp-client.modules.gui.window',
                          'openerp-client.modules.gui.window.view_sel',
                          'openerp-client.modules.gui.window.view_tree',
                          'openerp-client.modules.spool',
                          'openerp-client.printer',
                          'openerp-client.tools',
                          'openerp-client.tinygraph',
                          'openerp-client.widget',
                          'openerp-client.widget.model',
                          'openerp-client.widget.screen',
                          'openerp-client.widget.view',
                          'openerp-client.widget.view.form_gtk',
                          'openerp-client.widget.view.tree_gtk',
                          'openerp-client.widget.view.graph_gtk',
                          'openerp-client.widget.view.calendar_gtk',
                          'openerp-client.widget.view.gantt_gtk',
                          'openerp-client.widget.view.diagram_gtk',
                          'openerp-client.widget_search',
                          'openerp-client.SpiffGtkWidgets',
                          'openerp-client.SpiffGtkWidgets.Calendar',
                          'openerp-client.plugins'] + list(find_plugins()),
      package_dir      = {'openerp-client': 'bin'},
      options = options,
      install_requires = [
          'lxml',
          'pytz',
          'python-dateutil',
      ],
      **complementary_arguments
)

if has_py2exe:
    # Sometime between pytz-2008a and pytz-2008i common_timezones started to
    # include only names of zones with a corresponding data file in zoneinfo.
    # pytz installs the zoneinfo directory tree in the same directory
    # as the pytz/__init__.py file. These data files are loaded using
    # pkg_resources.resource_stream. py2exe does not copy this to library.zip so
    # resource_stream can't find the files and common_timezones is empty when
    # read in the py2exe executable.
    # This manually copies zoneinfo into the zip. See also
    # http://code.google.com/p/googletransitdatafeed/issues/detail?id=121
    import pytz
    import zipfile
    # Make sure the layout of pytz hasn't changed
    assert (pytz.__file__.endswith('__init__.pyc') or
            pytz.__file__.endswith('__init__.py')), pytz.__file__
    zoneinfo_dir = os.path.join(os.path.dirname(pytz.__file__), 'zoneinfo')
    # '..\\Lib\\pytz\\__init__.py' -> '..\\Lib'
    disk_basedir = os.path.dirname(os.path.dirname(pytz.__file__))
    zipfile_path = os.path.join(options['py2exe']['dist_dir'], 'library.zip')
    z = zipfile.ZipFile(zipfile_path, 'a')

    for absdir, directories, filenames in os.walk(zoneinfo_dir):
        assert absdir.startswith(disk_basedir), (absdir, disk_basedir)
        zip_dir = absdir[len(disk_basedir):]
        for f in filenames:
            z.write(os.path.join(absdir, f), os.path.join(zip_dir, f))

    z.close()
