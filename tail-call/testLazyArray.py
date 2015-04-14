#!/usr/bin/python

import unittest
import numpy as np

from numpy.testing import assert_array_equal, assert_equal

from lazyArray import LazyArray


class TestLazyArray(unittest.TestCase):
    def setUp(self):
        shape = (12, 13, 14)
        dtype = np.uint8().dtype
        x = np.random.randint(0, 256, size=shape).astype(dtype)
        x[0, 0, 0] = 0
        creator = lambda: x.copy()
        self.shape = shape
        self.dtype = dtype
        self.creator = creator
        self.x = x

    def testInheritance(self):
        la = LazyArray(self.creator, self.shape, self.dtype)
        assert hasattr(la, "_LazyArray__TESTATTRIBUTE")
        size = la._LazyArray__TESTATTRIBUTE
        assert_equal(size, 0)

        assert isinstance(la, np.ndarray)
        assert_array_equal(la.shape, self.shape)
        assert la.dtype == self.dtype
        # should still be LazyArray now
        assert hasattr(la, "_LazyArray__TESTATTRIBUTE")
        assert isinstance(la, LazyArray)

    def testInitFromAttribute(self):
        la = LazyArray(self.creator, self.shape, self.dtype)
        assert hasattr(la, "_LazyArray__TESTATTRIBUTE")
        size = la._LazyArray__TESTATTRIBUTE
        assert_equal(size, 0)

        attr = la.data
        assert not hasattr(la, "_LazyArray__TESTATTRIBUTE")
        assert not isinstance(la, LazyArray)
        assert_array_equal(la, self.x)

    def testInitFromSetitem(self):
        la = LazyArray(self.creator, self.shape, self.dtype)
        assert hasattr(la, "_LazyArray__TESTATTRIBUTE")
        size = la._LazyArray__TESTATTRIBUTE
        assert_equal(size, 0)

        la[0, 0, 0] = 42
        assert not hasattr(la, "_LazyArray__TESTATTRIBUTE")
        assert not isinstance(la, LazyArray)
        y = self.x
        y[0, 0, 0] = 42
        assert_array_equal(la, self.x)

    def testInitFromGetitem(self):
        la = LazyArray(self.creator, self.shape, self.dtype)
        assert hasattr(la, "_LazyArray__TESTATTRIBUTE")
        size = la._LazyArray__TESTATTRIBUTE
        assert_equal(size, 0)

        y = la[0, 0, 0]
        assert not hasattr(la, "_LazyArray__TESTATTRIBUTE")
        assert not isinstance(la, LazyArray)
        assert_array_equal(y, 0)

    def testInitFromMethod(self):
        la = LazyArray(self.creator, self.shape, self.dtype)
        assert hasattr(la, "_LazyArray__TESTATTRIBUTE")
        size = la._LazyArray__TESTATTRIBUTE
        assert_equal(size, 0)

        la.sort()
        assert not hasattr(la, "_LazyArray__TESTATTRIBUTE")
        y = self.x
        y.sort()
        assert_array_equal(la, y)

    def testInitFromView(self):
        la = LazyArray(self.creator, self.shape, self.dtype)
        assert hasattr(la, "_LazyArray__TESTATTRIBUTE")
        size = la._LazyArray__TESTATTRIBUTE
        assert_equal(size, 0)

        la2 = la.view(np.ndarray)
        assert not hasattr(la, "_LazyArray__TESTATTRIBUTE")
        assert_array_equal(la2, self.x)
