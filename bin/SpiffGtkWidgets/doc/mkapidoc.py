#!/usr/bin/env python
# Generates the API documentation.
import os, re, sys

doc_dir  = 'api'
doc_file = '../src/SpiffGtkWidgets/*'

os.system('epydoc ' + ' '.join(['--html',
                                '--parse-only',
                                '--no-private',
                                '--no-source',
                                '--no-frames',
                                '--inheritance=grouped',
                                '-v',
                                '-o %s' % doc_dir, doc_file]))
