#!/usr/bin/python

import numpy as np

from lazyflow.graph import Graph, InputSlot, OutputSlot
from lazyflow.operator import Operator

class OpTest(Operator):
    A = InputSlot()
    B = OutputSlot()
    
    def __init__(self, *args, **kwargs):
        super(OpTest, self).__init__(*args, **kwargs)
        self.B.connect(self.A)
        
    def propagateDirty(self, slot, subindex, roi):
        pass

if __name__ == "__main__":
    
    op = OpTest(graph=Graph())
    
    print("Test 1:")
    op.A.setValue(np.zeros((3,3)))
    out = op.B[...].wait()
    print(out)
    
    print("Test 2:")
    op.A.setValue([[0,0],[1,1]])
    out = op.B[...].wait()
    print(out)
    
