#!/usr/bin/python

import time

import numpy as np
import vigra

from lazyflow.graph import Graph
from lazyflow.operators import OpArrayCache, OpArrayPiper
import lazyflow.operators.opArrayCache
from lazyflow.drtile import drtile

from matplotlib import pyplot as plt

def toggle(drtile_enabled):
    if drtile_enabled:
        lazyflow.operators.opArrayCache.has_drtile = True
    else:
        lazyflow.operators.opArrayCache.has_drtile = False


def getVolume(shape):
    x = np.random.randint(0, 256, size=shape).astype(np.uint8)
    x = vigra.taggedView(x, axistags="xy")
    return x


class Timer(object):
    def __init__(self, benchmarkName):
        self._name = benchmarkName

    def __enter__(self):
        self._t = time.time()

    def __exit__(self, *args, **kwargs):
        t = time.time()
        self.result = t-self._t
        print("{}: {:.3}s".format(self._name, self.result))


def sideBySide(shape=(256, 256)):
    res = []
    for t in (True, False):
        g = Graph()
        pipe = OpArrayPiper(graph=g)
        op = OpArrayCache(graph=g)
        op.blockShape.setValue((128, 128))
        op.Input.connect(pipe.Output)
        toggle(t)
        vol = getVolume(shape)
        pipe.Input.setValue(vol)
        tmr = Timer("has_drtile={}".format(t)) 
        with tmr:
            out = op.Output[...].wait()
        res.append(tmr.result)
    return res


if __name__ == "__main__":
    shapes =[(128, n*128) for n in range(1, 17)]
    ns = np.arange(1, 17)
    ts = np.asarray([sideBySide(shape) for shape in shapes])

    plt.figure()
    plt.hold(True)
    plt.plot(ns, ts[:, 0], 'b')
    plt.plot(ns, ts[:, 1], 'r')
    plt.legend(("drtile", "no drtile"), "upper left")
    plt.xlabel("number of 128x128 blocks")
    plt.ylabel("time for piping [s]")
    plt.show()
