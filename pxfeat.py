# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 16:18:13 2015

@author: burger
"""

import numpy as np
import vigra

from lazyflow.graph import Graph
from lazyflow.operators import OpPixelFeaturesPresmoothed
from lazyflow.utility.testing import OpArrayPiperWithAccessCount

if __name__ == "__main__":
    g = Graph()

    x = np.zeros((5, 100, 120, 150, 3)).astype(np.uint8)
    x = vigra.taggedView(x, axistags='txyzc')

    pipe = OpArrayPiperWithAccessCount(graph=g)
    pipe.Input.meta.ideal_blockshape = (1, 20, 30, 25, 3)
    pipe.Input.setValue(x)

    op = OpPixelFeaturesPresmoothed(graph=g)
    op.Input.connect(pipe.Output)
    op.Scales.setValue((.7, 1.0, 2.0, 3.0, 4.0))
    op.FeatureIds.setValue(op.DefaultFeatureIds)
    op.Matrix.setValue(np.ones((6, 5)))

    print(op.Output.meta.ideal_blockshape)

    op.Output[2, 30:70, 40:78, :].wait()
    print(pipe.requests.pop())

    # 1   2   3   4
    # 7  10  14  17