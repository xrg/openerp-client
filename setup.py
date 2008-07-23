# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 Tiny SPRL (http://tiny.be) All Rights Reserved.
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
###############################################################################
# setup from TinERP
#   taken from straw http://www.nongnu.org/straw/index.html
#   taken from gnomolicious http://www.nongnu.org/gnomolicious/
#   adapted by Nicolas Évrard <nicoe@altern.org>

import imp
import sys
import os
import glob

from stat import ST_MODE

from distutils.file_util import copy_file
from distutils.core import setup
from mydistutils import L10nAppDistribution

if os.name == 'nt':
    import py2exe

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bin"))

opj = os.path.join

execfile(opj('bin', 'release.py'))


# get python short version
py_short_version = '%s.%s' % sys.version_info[:2]

required_modules = [('gtk', 'gtk python bindings'),
                    ('gtk.glade', 'glade python bindings'),
                    ('mx.DateTime', 'date and time handling routines for Python')]

def check_modules():
    ok = True
    for modname, desc in required_modules:
        try:
            exec('import %s' % modname)
        except ImportError:
            ok = False
            print 'Error: python module %s (%s) is required' % (modname, desc)

    if not ok:
        sys.exit(1)

def data_files():
    '''Build list of data files to be installed'''
    files = []
    if os.name == 'nt':
        import matplotlib
        datafiles = matplotlib.get_py2exe_datafiles()
        if isinstance(datafiles, list):
            files.extend(datafiles)
        else:
            files.append(datafiles)
        os.chdir('bin')
        for (dp,dn,names) in os.walk('themes'):
            if '.svn' in dn:
                dn.remove('.svn')
            files.append((dp, map(lambda x: opj('bin', dp,x), names)))
        for (dp, dn, names) in os.walk('share\\locale'):
            if '.svn' in dn:
                dn.remove('.svn')
            files.append((dp, map(lambda x: opj('bin', dp, x), names)))
        os.chdir('..')
        files.append((".",["bin\\terp.glade", 'bin\\tipoftheday.txt', 'doc\\README.txt']))
        files.append(("pixmaps", glob.glob("bin\\pixmaps\\*.*")))
        files.append(("po", glob.glob("bin\\po\\*.*")))
        files.append(("icons", glob.glob("bin\\icons\\*.png")))
        files.append(("share\\locale", glob.glob("bin\\share\\locale\\*.*")))
    else:
        files.append((opj('share','man','man1',''),['man/tinyerp-client.1']))
        files.append((opj('share','doc', 'tinyerp-client-%s' % version), [f for
            f in glob.glob('doc/*') if os.path.isfile(f)]))
        files.append((opj('share', 'pixmaps', 'tinyerp-client'),
            glob.glob('bin/pixmaps/*.png')))
        files.append((opj('share', 'pixmaps', 'tinyerp-client', 'icons'),
            glob.glob('bin/icons/*.png')))
        files.append((opj('share', 'tinyerp-client'), ['bin/terp.glade',
            'bin/tipoftheday.txt']))
    return files

included_plugins = ['workflow_print']

def find_plugins():
    for plugin in included_plugins:
        path=opj('bin', 'plugins', plugin)
        for dirpath, dirnames, filenames in os.walk(path):
            if '__init__.py' in filenames:
                modname = dirpath.replace(os.path.sep, '.')
                yield modname.replace('bin', 'tinyerp-client', 1)

def translations():
    trans = []
    dest = 'share/locale/%s/LC_MESSAGES/%s.mo'
    for po in glob.glob('bin/po/*.po'):
        lang = os.path.splitext(os.path.basename(po))[0]
        trans.append((dest % (lang, name), po))
    return trans

check_modules()

# create startup script
start_script = \
"#!/bin/sh\n\
cd %s/lib/python%s/site-packages/tinyerp-client\n\
exec %s ./tinyerp-client.py $@" % (sys.prefix, py_short_version, sys.executable)
# write script
f = open('tinyerp-client', 'w')
f.write(start_script)
f.close()

if os.name <> 'nt' and sys.argv[1] == 'build_po':
    os.system('(cd bin ; find . -name \*.py && find . -name \*.glade | xargs xgettext -o po/%s.pot)' % name)
    for file in ([ os.path.join('bin', 'po', fname) for fname in os.listdir('bin/po') ]):
        if os.path.isfile(file):
            os.system('msgmerge --update --backup=off %s bin/po/%s.pot' % (file, name))
    sys.exit()

options = {"py2exe": {"compressed": 1,
                      "optimize": 2,
                      "packages": ["encodings","gtk", "matplotlib", "pytz"],
                      "includes": "pango,atk,gobject,cairo,atk,pangocairo",
                      "excludes": ["Tkinter", "tcl", "TKconstants"],
                      "dll_excludes": [
                          "iconv.dll","intl.dll","libatk-1.0-0.dll",
                          "libgdk_pixbuf-2.0-0.dll","libgdk-win32-2.0-0.dll",
                          "libglib-2.0-0.dll","libgmodule-2.0-0.dll",
                          "libgobject-2.0-0.dll","libgthread-2.0-0.dll",
                          "libgtk-win32-2.0-0.dll","libpango-1.0-0.dll",
                          "libpangowin32-1.0-0.dll",
                          "wxmsw26uh_vc.dll",],
                      }
           }

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
      scripts          = ['tinyerp-client'],
      packages         = ['tinyerp-client', 'tinyerp-client.common', 
                          'tinyerp-client.modules', 'tinyerp-client.modules.action',
                          'tinyerp-client.modules.gui',
                          'tinyerp-client.modules.gui.window',
                          'tinyerp-client.modules.gui.window.view_sel',
                          'tinyerp-client.modules.gui.window.view_tree',
                          'tinyerp-client.modules.spool',
                          'tinyerp-client.printer', 'tinyerp-client.tools',
                          'tinyerp-client.tinygraph',
                          'tinyerp-client.widget',
                          'tinyerp-client.widget.model',
                          'tinyerp-client.widget.screen',
                          'tinyerp-client.widget.view',
                          'tinyerp-client.widget.view.form_gtk',
                          'tinyerp-client.widget.view.tree_gtk',
                          'tinyerp-client.widget.view.graph_gtk',
                          'tinyerp-client.widget.view.calendar_gtk',
                          'tinyerp-client.widget_search',
                          'tinyerp-client.plugins'] + list(find_plugins()),
      package_dir      = {'tinyerp-client': 'bin'},
      distclass = os.name <> 'nt' and L10nAppDistribution or None,
      windows=[{"script":"bin\\tinyerp-client.py", "icon_resources":[(1,"bin\\pixmaps\\tinyerp.ico")]}],
      options = options,
      )



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

