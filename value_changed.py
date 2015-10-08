


from lazyflow.operator import Operator, InputSlot, OutputSlot
from lazyflow.graph import Graph

class MyOp(Operator):
    Input = InputSlot()

    _InnerOutput = OutputSlot()
    _AnotherInnerOutput = OutputSlot()
    Output = OutputSlot()

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.Output.connect(self.Input)
        self._AnotherInnerOutput.connect(self._InnerOutput)

    def setupOutputs(self):
        self._InnerOutput.meta.assignFrom(self.Input.meta)

    def propagateDirty(self, slot, subindex, roi):
        pass



def valueChanged(slot):
    if slot.ready():
        print("Slot {} changed to value {}".format(slot.name, slot.value))
    else:
        print("Slot {} became unready".format(slot.name))

if __name__ == "__main__":
    op = MyOp(graph=Graph())
    op.Output.notifyMetaChanged(valueChanged)

    # not here
    print("Setting 1 to Input")
    op.Input.setValue(1)

    # also not here
    op._AnotherInnerOutput.notifyMetaChanged(valueChanged)
    print("Setting 2 to _innerOutput")
    op._InnerOutput.setValue(2)

    # guess
    print("Disconnecting AnotherInnerOutput")
    op._AnotherInnerOutput.disconnect()
    print("Setting 3 to AnotherInnerOutput")
    op._AnotherInnerOutput.setValue(3)
