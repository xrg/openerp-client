#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from mydistutils import setup

opj = os.path.join

name = 'tinyerp-client'
version = '4.0.0'

# get python short version
py_short_version = '%s.%s' % sys.version_info[:2]

required_modules = [('gtk', 'gtk python bindings'),
                    ('gtk.glade', 'glade python bindings')]

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
    files = [(opj('share','man','man1',''),['man/tinyerp-client.1']),
             (opj('share','doc', 'tinyerp-client-%s' % version), 
              [f for f in glob.glob('doc/*') if os.path.isfile(f)]),
             (opj('share', 'pixmaps', 'tinyerp-client'),
              glob.glob('pixmaps/*.png') + glob.glob('bin/*.png')),
             (opj('share', 'pixmaps', 'tinyerp-client', 'icons'),
                     glob.glob('bin/icons/*.png')),
             (opj('share', 'tinyerp-client'),
              ['bin/terp.glade', 'bin/tipoftheday.txt'])]
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

long_desc = '''\
Tiny ERP is a complete ERP and CRM. The main features are accounting (analytic
and financial), stock management, sales and purchases management, tasks
automation, marketing campaigns, help desk, POS, etc. Technical features include
a distributed server, flexible workflows, an object database, a dynamic GUI,
customizable reports, and SOAP and XML-RPC interfaces.
'''

classifiers = """\
Development Status :: 5 - Production/Stable
License :: OSI Approved :: GNU General Public License (GPL)
Programming Language :: Python
"""

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

# todo: use 
command = sys.argv[1]

setup(name             = name,
      version          = version,
      description      = "Tiny's ERP Client",
      long_description = long_desc,
      url              = 'http://tinyerp.com',
      author           = 'Tiny.be',
      author_email     = 'info@tiny.be',
      classifiers      = filter(None, classifiers.splitlines()),
      license          = 'GPL',
      data_files       = data_files(),
      translations     = translations(),
      pot_file         = 'bin/po/terp-msg.pot',
      scripts          = ['tinyerp-client'],
      packages         = ['tinyerp-client', 'tinyerp-client.common', 
                          'tinyerp-client.modules', 'tinyerp-client.modules.action',
                          'tinyerp-client.modules.gui',
                          'tinyerp-client.modules.gui.window',
                          'tinyerp-client.modules.gui.window.view_sel',
                          'tinyerp-client.modules.gui.window.view_tree',
                          'tinyerp-client.modules.spool',
                          'tinyerp-client.printer', 'tinyerp-client.tools',
                          'tinyerp-client.widget',
                          'tinyerp-client.widget.model',
                          'tinyerp-client.widget.screen',
                          'tinyerp-client.widget.view',
                          'tinyerp-client.widget.view.form_gtk',
                          'tinyerp-client.widget.view.tree_gtk',
                          'tinyerp-client.widget_search',
                          'tinyerp-client.plugins'] + list(find_plugins()),
      package_dir      = {'tinyerp-client': 'bin'},
      )


# vim:expandtab:tw=80
