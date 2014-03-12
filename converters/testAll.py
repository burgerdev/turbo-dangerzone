
import unittest

import converter


class TestAll(unittest.TestCase):

    def testSimple(self):
        c = converter.MyClass()
        c.foo(1, 2)

    @unittest.skip("not expected to work")
    def testToPython(self):
        c = converter.MyClass()
        v = c.bar(1, 2, 3)

    def testFromPython(self):
        c = converter.MyClass()
        c.baz((1, 2, 3))
