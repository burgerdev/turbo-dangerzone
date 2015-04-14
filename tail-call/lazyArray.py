#!/usr/bin/python

import numpy as np
import copy

EXC = ("_LazyArray__initialized",
       "_LazyArray__initialize",
       "_LazyArray__creator",
       "_LazyArray__shape",
       "__array_finalize__")

NP_EXC = ("dtype",
          "resize",
          "shape")


class LazyArray2(np.ndarray, object):

    def __new__(cls, creator, shape, dtype):
        return np.ndarray.__new__(cls, shape, dtype=dtype)

    def __init__(self, creator, shape, dtype):
        assert callable(creator)
        self.__creator = creator
        self.__shape = shape
        self.__initialized = False

    def __getattribute__(self, name):
        print("GETATTR CALL: {}".format(name))
        if name == "shape" and not self.__initialized:
            return self.__shape
        elif name == "_LazyArray__TESTATTRIBUTE":
            if self.__initialized:
                raise AttributeError
            else:
                print("RETURNING TESTATTRIBUTE")
                return "TESTATTRIBUTE"
        elif name in EXC:
            print("returning from object")
            return object.__getattribute__(self, name)
        elif name in NP_EXC or name.startswith("__array"):
            print("returning from ndarray directly")
            return np.ndarray.__getattribute__(self, name)
        else:
            print("returning from ndarray with initialization")
            self.__initialize()
            return np.ndarray.__getattribute__(self, name)

    def __initialize(self):
        print("IN INITIALIZE()")
        if not self.__initialized:
            print("INITIALIZING")
            self.__initialized = True
            self.resize(self.__shape)
            self[:] = self.__creator()
        #self.__class__ = np.ndarray


class _ndarray(np.ndarray):
    pass


class LazyArray(_ndarray):

    def __new__(cls, creator, shape, dtype):
        return np.ndarray.__new__(cls, (0,), dtype=dtype)

    def __init__(self, creator, shape, dtype):
        assert callable(creator)
        self.__creator = creator
        self.__shape = shape
        self.__initialized = False

    def __getattribute__(self, name):
        print("GETATTR CALL: {}".format(name))
        if name == "shape":
            # override ndarray.shape
            return self.__shape
        elif name == "_LazyArray__TESTATTRIBUTE":
            # for testing if array is replaced
            return super(LazyArray, self).size
        elif name in EXC:
            # access to our own class-members
            return object.__getattribute__(self, name)
        elif name in NP_EXC or name.startswith("__array"):
            # special numpy functions that must not trigger
            # initialization
            return np.ndarray.__getattribute__(self, name)
        else:
            # unknown data is requested, we need to initialize
            self.__initialize()
            return _ndarray.__getattribute__(self, name)

    def __setitem__(self, key, value):
        self.__initialize()
        _ndarray.__setitem__(self, key, value)

    def __getitem__(self, key):
        self.__initialize()
        return _ndarray.__getitem__(self, key)

    def __initialize(self):
        self.__initialized = True
        self.resize(self.__shape, refcheck=False)
        self[:] = self.__creator()
        self.__class__ = _ndarray
