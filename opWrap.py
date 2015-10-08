

import numpy as np
import vigra

from lazyflow.graph import Graph
from lazyflow.operator import Operator, InputSlot, OutputSlot
from lazyflow.operatorWrapper import OperatorWrapper
from lazyflow.operators import OpArrayPiper

from lazyflow.operators.generic import OpMultiArraySlicer, OpMultiArrayStacker

from ilastik.applets.thresholdTwoLevels import OpThresholdTwoLevels


class TestOp(Operator):
    Input = InputSlot()
    Output = OutputSlot()

    def __init__(self, *args, **kwargs):
        super(TestOp, self).__init__(*args, **kwargs)

    def setupOutputs(self):
        self.Output.meta.assignFrom(self.Input.meta)
        print(self.Input.meta.getTaggedShape())


class Printer(Operator):

    Input = InputSlot()
    Compare = InputSlot()
    Output = OutputSlot()

    def __init__(self, *args, **kwargs):
        super(Printer, self).__init__(*args, **kwargs)

    def setupOutputs(self):
        d1 = self.Input.meta.getTaggedShape()
        d2 = self.Compare.meta.getTaggedShape()
        for k in d1:
            assert d1[k] == d2[k], "{} vs. {}".format(d1, d2)

    def propagateDirty(self, slot, subindex, roi):
        pass
        #print("PROPAGATEDIRTY")
        #print("dirty: {}".format(str(roi)))



def test1():
    vol = np.zeros((1, 2, 3, 4, 5), dtype=np.uint8)
    vol1 = vigra.taggedView(vol, axistags='txyzc')
    vol2 = vigra.taggedView(vol, axistags='czyxt')

    g = Graph()

    pipe1 = OpArrayPiper(graph=g)
    pipe1.Input.setValue(vol1)
    pipe2 = OpArrayPiper(graph=g)
    pipe2.Input.setValue(vol2)

    slicer = OpMultiArraySlicer(graph=g)
    slicer.AxisFlag.setValue('c')
    op = OperatorWrapper(TestOp, graph=g)
    op.Input.connect(slicer.Slices)
    stacker = OpMultiArrayStacker(graph=g)
    stacker.AxisFlag.setValue('c')
    stacker.Images.connect(op.Output)

    stacker.AxisIndex.setValue(0)
    slicer.Input.connect(pipe1.Output)
    print(stacker.Output.meta.getTaggedShape())

    print()

    stacker.AxisIndex.setValue(0)
    slicer.Input.connect(pipe2.Output)
    print(stacker.Output.meta.getTaggedShape())
    
def test2():
    vol = np.zeros((2, 3, 4, 5, 6), dtype=np.uint8)
    vol1 = vigra.taggedView(vol, axistags='txyzc')
    vol2 = vigra.taggedView(vol, axistags='czyxt')

    g = Graph()

    pipe1 = OpArrayPiper(graph=g)
    pipe1.Input.setValue(vol1)
    pipe2 = OpArrayPiper(graph=g)
    pipe2.Input.setValue(vol2)

    op = OpThresholdTwoLevels(graph=g)
    printer = Printer(graph=g)
    printer.Input.connect(op.Output)

    op.InputImage.connect(pipe1.Output)
    #print(op.Output.meta.getTaggedShape())
    #print(op.CachedOutput.meta.getTaggedShape())

    print("")

    #op.InputImage.connect(pipe2.Output)
    op.InputImage.meta.axistags = vol2.axistags
    op.InputImage._sig_changed()
    #print(op.Output.meta.getTaggedShape())
    #print(op.CachedOutput.meta.getTaggedShape())

if __name__ == "__main__":
    test2()

