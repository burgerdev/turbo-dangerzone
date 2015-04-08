
import time

import numpy as np
import vigra

from lazyflow.operator import Operator, InputSlot, OutputSlot
from lazyflow.graph import Graph

from lazyflow.operatorWrapper import OperatorWrapper

from lazyflow.operators import OpMultiArraySlicer2, OpMultiArrayStacker


class OpZero(Operator):
    Shape = InputSlot()
    Nothing = InputSlot(optional=True)
    Output = OutputSlot()

    def setupOutputs(self):
        self.Output.meta.shape = self.Shape.value
        self.Output.meta.dtype = np.uint8
        self.Output.meta.axistags = vigra.defaultAxistags('txy')

    def execute(self, slot, subindex, roi, result):
        result[...] = 0

    def propagateDirty(self, slot, subindex, roi):
        self.Output.setDirty(slice(None))


class OpSimple(Operator):
    '''
    stateless
    '''

    Input = InputSlot()
    Output = OutputSlot()

    def setupOutputs(self):
        self.Output.meta.assignFrom(self.Input.meta)

    def propagateDirty(self, slot, subindex, roi):
        self.Output.setDirty(roi)

    def execute(self, slot, subindex, roi, result):
        result[...] = self.Input.get(roi).wait() + 1


class MinTimer(object):
    '''
    keep track of the minimal elapsed time of a series of time
    measurements
    (note that the minimum of a time series tells us more about the
    actual code complexity than the average, which can be biased by
    cpu spikes etc.)
    '''
    t = np.inf
    _t = 0
    def __enter__(self):
        self._t = -time.time()

    def __exit__(self, *args):
        self._t += time.time()
        if self._t < self.t:
            self.t = self._t


def create(n):
    g = Graph()
    opProvider = OpZero(graph=g)
    slicer = OpMultiArraySlicer2(graph=g)
    stacker = OpMultiArrayStacker(graph=g)

    wrapped = OperatorWrapper(OpSimple, graph=g)

    stacker.Images.connect(wrapped.Output)
    stacker.AxisFlag.setValue('t')

    wrapped.Input.connect(slicer.Slices)

    slicer.Input.connect(opProvider.Output)
    slicer.AxisFlag.setValue('t')

    opProvider.Shape.setValue((n, 1024, 1024))

    return opProvider, slicer, wrapped, stacker

def timeSetup(lenSeries=10):
    r = []
    for n in range(1, 20):
        prov = create(n)[0]
        T = MinTimer()
        for s in range(lenSeries):
            with T:
                prov.Nothing.setValue(s % 2)
        r.append((n, T.t))
    return np.asarray(r)


if __name__ == "__main__":
    from matplotlib import pyplot as plt
    plt.xkcd()
    x = timeSetup()
    plt.plot(x[:, 0], x[:, 1])
    plt.xlabel("# time slices")
    plt.ylabel("setupOutputs() time [s]")
    plt.title("setup time for a single wrapped operator")
    plt.show()

