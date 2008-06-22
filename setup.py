from setuptools import setup, find_packages
from os.path    import dirname, join
srcdir = join(dirname(__file__), 'src')
setup(name             = 'Spiff Gtk Widgets',
      version          = '1.9.0',
      description      = 'A collection of useful Gtk widgets',
      long_description = \
"""
Spiff Gtk Widgets contains a number of Gtk widgets that are used 
by other Spiff components.
""",
      author           = 'Samuel Abels',
      author_email     = 'cheeseshop.python.org@debain.org',
      license          = 'GPLv2',
      package_dir      = {'': srcdir},
      packages         = [p for p in find_packages(srcdir)],
      install_requires = [],
      keywords         = 'spiff gtk widgets textview annotations',
      url              = 'http://code.google.com/p/spiff/',
      classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])
