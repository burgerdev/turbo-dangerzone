#!/usr/bin/python

import os
import sys

import numpy as np
from collections import OrderedDict

with_plot = False

if with_plot:
    from matplotlib import pyplot as plt


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: histdump.py <core-file>")
        sys.exit(1)

    fn = sys.argv[1]
    if fn == "--":
        f = sys.stdin
    else:
        f = open(fn, 'rb')
    x = np.fromfile(f, dtype=np.uint8)
    f.close()

    bins = np.arange(0, 256)
    y, bins = np.histogram(x, bins)

    inds = np.argsort(y)
    common = OrderedDict(zip(reversed(bins[inds][-10:]),
                             reversed(y[inds][-10:])))

    print("Most common bytes (decreasing):")
    for key in common:
        print("{:02X}:\t{:.1e}".format(key, common[key]))

    if with_plot:
        plt.hist(x, bins)
        plt.show()

