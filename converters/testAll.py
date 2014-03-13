
import unittest

#import vigra

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

    def testInit(self):
        c = converter.MyOtherClass((42, 43, 44))

    def testTemplated(self):
        c = converter.TemplatedClass(.5)
        c = converter.TemplatedClass(15)

    def testFailing(self):
        with self.assertRaises(Exception):
            c = converter.TemplatedClass((3,4))



