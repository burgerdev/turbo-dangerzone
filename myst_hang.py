import numpy
import vigra
np = numpy

from lazyflow.graph import Graph
from lazyflow.operators import Op5ifyer
from ilastik.applets.thresholdTwoLevels.opThresholdTwoLevels \
    import OpThresholdTwoLevels, OpSelectLabels

from ilastik.applets.thresholdTwoLevels.opThresholdTwoLevels\
    import _OpThresholdOneLevel as OpThresholdOneLevel
from ilastik.applets.thresholdTwoLevels.opThresholdTwoLevels\
    import _OpThresholdTwoLevels as OpThresholdTwoLevels5d

import ilastik.ilastik_logging
ilastik.ilastik_logging.default_config.init()
import unittest


vol = vigra.impex.readImage('/home/burger/hci/hci-data/test/2d_cells_apoptotic_1channel.png')
vol = vol.astype(np.uint8)
vol = vigra.taggedView(vol, axistags='xyc')

print(np.histogram(vol))

g = Graph()
oper = OpThresholdTwoLevels(graph=g)
oper.InputImage.setValue(vol)

print("setting drange")
oper.InputImage.meta.drange = (0,255)
#oper.MinSize.setValue(1)
#oper.MaxSize.setValue(np.prod(self.vol.shape[1:]))
#oper.HighThreshold.setValue(.7)
#oper.LowThreshold.setValue(.3)
oper.SingleThreshold.setValue(.5)
#oper.SmootherSigma.setValue({'x': 0, 'y': 0, 'z': 0})
oper.CurOperator.setValue(0)

print("requesting output")
oper.SingleThreshold.setValue(.3)

output = oper.Output[:].wait()
output = vigra.taggedView(output, axistags=oper.Output.meta.axistags)

print(np.histogram(output))