# -*- coding: utf-8 -*-
"""
Created on Thu Feb 26 19:32:41 2015

@author: markus
"""

import numpy as np
import vigra

from lazyflow.graph import Graph
from lazyflow.operators.opCompressedCache import OpCompressedCache
from lazyflow.operators.valueProviders import OpArrayPiper
from timeit import timeit, repeat

def genOp():
    graph = Graph()
    pipe = OpArrayPiper(graph=graph)
    op = OpCompressedCache(graph=graph)
    op.Input.connect(pipe.Output)
    return pipe, op

x = np.random.randint(0, 255, size=(1024, 64, 64)).astype(np.uint8)
v = vigra.taggedView(x, axistags='zyx')
w = vigra.taggedView(x, axistags='tyx')

def runSingle(vol, N=1, funny=True):
    pipe, op = genOp()
    op.with_funny_stuff = funny
    pipe.Input.setValue(vol)
    for n in range(N):
        for i in range(len(vol)):
            op.Output[i, ...].wait()

def runDemoBenchmark():
    r = timeit("runSingle(v[0:64, ...], N=5)", number=1,
               setup="from __main__ import runSingle, v")
    print(r)

def runBenchmark():
    print("Old style xyz")
    r = repeat("runSingle(v)", repeat=3, number=1,
               setup="from __main__ import runSingle, v")
    print(r)

    print("New style xyz")
    r = repeat("runSingle(v, funny=False)", repeat=3, number=1,
               setup="from __main__ import runSingle, v")
    print(r)

    print("Old style xyt")
    r = repeat("runSingle(w)", repeat=3, number=1,
               setup="from __main__ import runSingle, w")
    print(r)

    print("New style xyt")
    r = repeat("runSingle(w, funny=False)", repeat=3, number=1,
               setup="from __main__ import runSingle, w")
    print(r)

def runWithLog():
    import logging
    logging.basicConfig(level=logging.DEBUG)
    runSingle(v, N=1)
    print("=======================================================")
    runSingle(w, N=1)
    

if __name__ == "__main__":
    runBenchmark()
    # runDemoBenchmark()
    # runWithLog()