#!/usr/bin/python
import libmytest as test

import unittest


class God(test.God):

    def __init__(self):
        super(God, self).__init__()

    def answer(self):
        return 43


class Mighty(test.Mighty):
    def __init__(self):
        super(Mighty, self).__init__()

    def answer(self):
        return 43


class Tests(unittest.TestCase):
    def setUp(self):
        pass

    def testSimple(self):
        print(test.yay())

    def testMedium(self):
        t = test.Mighty()
        assert t.answer() == 42

    def testHard(self):
        bla = Mighty()
        assert bla.answer() == 43

        assert test.mycall(bla) == 43

    def testImpossible(self):
        with self.assertRaises(Exception):
            assert test.mycall(None) == 42

    def testGodMode(self):

        bla = God()
        assert bla.answer() == 43

        assert test.mycall(bla) == 43


