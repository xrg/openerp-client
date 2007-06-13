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

if os.name == 'nt':
    import py2exe

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bin"))

opj = os.path.join

execfile(opj('bin', 'release.py'))


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
              glob.glob('bin/pixmaps/*.png')),
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
    os.system('(cd bin ; find . -name \*.py | xargs xgettext -o po/%s.pot)' % name)
    for file in ([ os.path.join('bin', 'po', fname) for fname in os.listdir('bin/po') ]):
        print file
        if os.path.isfile(file):
            os.system('msgmerge --update --backup=off %s bin/po/%s.pot' % (file, name))
    sys.exit()


if os.name == 'nt':
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
    data_files = []
    import matplotlib
    data_files.append(matplotlib.get_py2exe_datafiles())

    os.chdir('bin')
    for (dp,dn,names) in os.walk('themes'):
        if '.svn' in dn:
            dn.remove('.svn')
        data_files.append((dp, map(lambda x: os.path.join('bin', dp,x), names)))
    os.chdir('..')

    data_files.append((".",["bin\\terp.glade","bin\\tinyerp_icon.png","bin\\tinyerp.png","bin\\flag.png", 'bin\\tipoftheday.txt', 'doc\\README.txt']))
    data_files.append(("pict",glob.glob("bin\\pict\\*.png")))
    data_files.append(("po",glob.glob("bin\\po\\*.*")))
    data_files.append(("icons",glob.glob("bin\\icons\\*.png")))

    setup(
        name="tinyerp-client",
        windows=[{"script":"bin\\tinyerp-client.py", "icon_resources":[(1,"pixmaps\\tinyerp.ico")]}],
        data_files = data_files,
        options = options,
        )
else:
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
