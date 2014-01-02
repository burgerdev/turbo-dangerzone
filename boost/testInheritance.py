#!/usr/bin/python
import libmytest as test

import unittest

class Tests(unittest.TestCase):
    def setUp(self):
        pass

    def testSimple(self):
        print(test.yay())

    def testMedium(self):
        t = test.Mighty()
        assert t.answer() == 42
    
    def testHard(self):
        class Bla(test.Mighty):
            def answer(self):
                return 43

        bla = Bla()
        assert bla.answer() == 43

        assert test.mycall(bla) == 43

    def testImpossible(self):
        with self.assertRaises(Exception):
            assert test.mycall(None) == 42

