from distutils.core import setup
import py2exe
import glob
import os
import sys

top_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(top_dir, "bin"))


options = {"py2exe": {"compressed": 1,
                      "optimize": 2,
                      "packages": ["encodings","gtk", "matplotlib", "pytz"],
                      "includes": "pango,atk,gobject,cairo,atk,pangocairo",
                      "excludes": ["Tkinter", "tcl"],
                      "dll_excludes": [
        "iconv.dll","intl.dll","libatk-1.0-0.dll",
        "libgdk_pixbuf-2.0-0.dll","libgdk-win32-2.0-0.dll",
        "libglib-2.0-0.dll","libgmodule-2.0-0.dll",
        "libgobject-2.0-0.dll","libgthread-2.0-0.dll",
        "libgtk-win32-2.0-0.dll","libpango-1.0-0.dll",
        "libpangowin32-1.0-0.dll",
        "wxmsw26uh_vc.dll", "tcl84.dll"], }}

         
version = '4.1.1'
opj = os.path.join

data_files = []
import matplotlib
data_files.append(matplotlib.get_py2exe_datafiles())

# inclusion of themes
os.chdir('bin')
for (dp,dn,names) in os.walk('themes'):
    #names = filter(lambda x: x[-4:] in ('.xml','.xsl','.sql') or x=='__terp__.py', names)
    #if len(names):
    if '.svn' in dn:
	dn.remove('.svn')
    data_files.append((dp, map(lambda x: os.path.join('bin', dp,x), names)))
os.chdir('..')

data_files.append((".",["bin/terp.glade","bin/tinyerp_icon.png","bin/tinyerp.png","bin/flag.png", 'bin/tipoftheday.txt', 'doc/README.txt']))
data_files.append(("pict",glob.glob("bin\\pict\\*.png")))
data_files.append(("po",glob.glob("bin\\po\\*.*")))
data_files.append(("icons",glob.glob("bin\\icons\\*.png")))

setup(
    name="tinyerp-client",
    windows=[{"script":"bin/tinyerp-client.py", "icon_resources":[(1,"tinyerp-icon.ico")]}],
    data_files = data_files,
    options = options,
    )
