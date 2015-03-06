
import timeit

import numpy as np
import vigra

from lazyflow.operator import Operator, InputSlot, OutputSlot
from lazyflow.graph import Graph

from lazyflow.operatorWrapper import OperatorWrapper

from lazyflow.operators import OpMultiArraySlicer2, OpMultiArrayStacker


class OpZero(Operator):
    Shape = InputSlot()
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


def runSingleWrapped(n, justSetup=True):
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

    if justSetup:
        return

def timeSetup():
    r = []
    for i in range(1, 20):
        stmt = "runSingleWrapped({})".format(i)
        t = timeit.timeit(
            stmt=stmt, number=1,
            setup="from timeWrapper import runSingleWrapped")
        r.append((i, t))

    # return np.asarray(r)

    for i in range(20, 300, 10):
        stmt = "runSingleWrapped({})".format(i)
        t = timeit.timeit(
            stmt=stmt, number=1,
            setup="from timeWrapper import runSingleWrapped")
        r.append((i, t))

    for i in range(300, 2000, 100):
        stmt = "runSingleWrapped({})".format(i)
        t = timeit.timeit(
            stmt=stmt, number=1,
            setup="from timeWrapper import runSingleWrapped")
        r.append((i, t))

    x = np.asarray(r)
    return x

if __name__ == "__main__":
    from matplotlib import pyplot as plt
    plt.xkcd()
    x = timeSetup()
    plt.plot(x[:, 0], x[:, 1])
    plt.xlabel("# time slices")
    plt.ylabel("setupOutputs() time [s]")
    plt.title("setup time for a single wrapped operator")
    plt.show()

