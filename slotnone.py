from lazyflow.operator import Operator, InputSlot, OutputSlot
from lazyflow.graph import Graph


class Operator2(Operator):
    ConfigSlot = InputSlot()
    Output = OutputSlot()

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    def setupOutputs(self):
        print("setting outputs")
        # this fails!
        # c = self.ConfigSlot.value

    def propagateDirty(self, slot, subindex, roi):
        pass


if __name__ == "__main__":
    g = Graph()
    op = Operator2(graph=g)

    print("Setting config slot")

    op.ConfigSlot.setValue(5)

    print("unsetting config slot")

    op.ConfigSlot.setValue(None)


