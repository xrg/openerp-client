import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

def suite():
    tests = ['testAnnotation']
    return unittest.TestSuite(map(AnnotationTest, tests))

import gtk
from SpiffGtkWidgets.AnnotatedTextView import Annotation

class AnnotationTest(unittest.TestCase):
    def testAnnotation(self):
        pass #FIXME

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
