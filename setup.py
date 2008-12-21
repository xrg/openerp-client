from setuptools import setup, find_packages
from os.path    import dirname, join
srcdir = join(dirname(__file__), 'src')
setup(name             = 'SpiffGtkWidgets',
      version          = '0.2.0',
      description      = 'A collection of useful Gtk widgets',
      long_description = \
"""
Spiff Gtk Widgets provides a collection of Gtk widgets:

  - An annotated text view
  - A calendar similar to Google's online calendar
""",
      author           = 'Samuel Abels',
      author_email     = 'cheeseshop.python.org@debain.org',
      license          = 'GPLv2',
      package_dir      = {'': srcdir},
      packages         = [p for p in find_packages(srcdir)],
      install_requires = [],
      keywords         = 'spiff gtk widgets textview annotations calendar',
      url              = 'http://code.google.com/p/spiff-gtkwidgets/',
      classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])
