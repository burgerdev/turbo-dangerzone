from lazycc import OpLazyCC

import unittest

import numpy as np
import vigra

from lazyflow.graph import Graph

class TestLazyCC(unittest.TestCase):
    def setUp(self):
        pass

    def testLabelingBasics(self):
        vol = np.zeros((140, 100, 10))
        vol = vol.astype(np.uint8)
        vol = vigra.taggedView(vol, axistags='xyz')
        labels = vol.copy()

        labels[:10, :10, 0:2]  = 1
        labels[20:70, 21:80, 0:4] = 2

        vol = np.where(labels>0, 1, 0).astype(np.uint8)

        op = OpLazyCC(graph=Graph())
        op.Input.setValue(vol)
        op.BlockShape.setValue((50,50,1))

        outFull = op.Output[...].wait()
        outFull = vigra.taggedView(outFull, axistags=op.Output.meta.axistags)

        assertEquivalentLabeling(labels, outFull)

    @unittest.skip("Not needed now")
    def testConsistency(self):
        vol = np.zeros((1000, 100, 10))
        vol = vol.astype(np.uint8)
        vol = vigra.taggedView(vol, axistags='xyz')
        labels = vol.copy()

        labels[:10, :10, 0:2]  = 1
        labels[20:70, 21:80, 0:4] = 2

        vol = np.where(labels>0, 1, 0).astype(np.uint8)

        op = OpLazyCC(graph=Graph())
        op.Input.setValue(vol)
        op.BlockShape.setValue((50,50,1))

        outBlock = op.Output[50:100, 50:100, 0].wait()
        outBlock = vigra.taggedView(outBlock, axistags=op.Output.meta.axistags)
        outFull = op.Output[...].wait()
        outFull = vigra.taggedView(outFull, axistags=op.Output.meta.axistags)

        assertEquivalentLabeling(labels, outFull)
        np.testing.assert_array_equal(outBlock, outFull[50:100, 50:100, 0])


## check if two label images have the same meaning
def assertEquivalentLabeling(vol_to_test, ground_truth):
    y = vol_to_test
    x = ground_truth
    assert np.all(x.shape == y.shape),\
        "Shapes do not agree ({} vs {})".format(x.shape, y.shape)

    # identify labels used in x
    labels = set(x.flat)
    for label in labels:
        if label == 0:
            continue
        idx = np.where(x == label)
        block = y[idx]
        # check that labels are the same
        an_index = [a[0] for a in idx]
        #print("Inspecting block of shape {} at".format(block.shape))
        #print(an_index)
        assert np.all(block == block[0]),\
            "Block at {} has multiple labels".format(an_index)
        # check that nothing else is labeled with this label
        m = block.size
        n = len(np.where(y == block[0])[0])
        assert m == n, "Label {} is used somewhere else.".format(label)


class MyTestLazyCC(TestLazyCC):
    def __init__(self):
        self.setUp()
    def run(self):
        self.testLabelingBasics()

if __name__ == "__main__":
    
    import cProfile, pstats, StringIO
    pr = cProfile.Profile()
    pr.enable()
    ### ACTUAL WORK ###
    test = MyTestLazyCC()
    test.testLabelingBasics()
    ### END WORK ###
    pr.disable()
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()
    
