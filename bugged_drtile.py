#!/usr/bin/python

import numpy as np
from lazyflow.drtile import drtile

def doc(x):
    y = np.where(x, 1, 128**3).astype(np.uint32)
    return drtile.test_DRTILE(y, 128**3).swapaxes(0,1)

def doc2(x):
    from lazyflow.drtile2 import drtile as drt
    return np.asarray(drt(x)).swapaxes(0, 1)

def getTilingTestCase():
    x = [[1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1],
         [1, 1, 0, 0, 1],
         [1, 1, 0, 0, 1],
         [0, 1, 1, 1, 1]]
    x = np.asarray(x, dtype=np.uint32)

    opt = [[1, 1, 2, 2, 4],
           [1, 1, 2, 2, 4],
           [1, 1, 0, 0, 4],
           [1, 1, 0, 0, 4],
           [0, 3, 3, 3, 4]]
    opt = np.asarray(opt, dtype=np.uint32)
    return x, opt

def tilingToArray(x, m=5, n=5):
    y = np.zeros((m, n), dtype=np.uint32)
    half = len(x)//2
    for i in range(x.shape[1]):
        start = x[:half, i]
        stop = x[half:, i]
        key = tuple([slice(a, b) for a, b in zip(start, stop)])
        y[key] = i+1
    return y


def demo():
    x, opt = getTilingTestCase()
    drtile_tiles = doc(x)
    new_tiles = doc2(x)
    print("Array to tile:")
    print(x)
    print("drtile result:")
    print(tilingToArray(drtile_tiles))
    print("optimal solution:")
    print(opt)
    print("new")
    print(tilingToArray(new_tiles))
    


if __name__ == "__main__":
    demo()
