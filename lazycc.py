from lazyflow.operator import Operator
from lazyflow.slot import InputSlot, OutputSlot
from lazyflow.rtype import SubRegion
from lazyflow.operators import OpCompressedCache

import numpy as np
import vigra

class OpLazyCC(Operator):
    Input = InputSlot()
    BlockShape = InputSlot()
    Background = InputSlot(value=0)
    Output = OutputSlot()

    def __init__(self, *args, **kwargs):
        super(OpLazyCC, self).__init__(*args, **kwargs)

    def setupOutputs(self):
        assert len(self.Input.meta.shape) == 3
        assert len(self.BlockShape.value) == 3
        assert self.Background.value == 0, "Not supported"
        allowedTypes = [np.uint8, np.uint32]
        assert self.Input.meta.dtype in allowedTypes
        labelType = np.uint32
        self.Output.meta.assignFrom(self.Input.meta)
        self.Output.meta.dtype = labelType

        bs = self._calcBlockShape()
        self._localUnionFinds = np.empty(bs, dtype=np.object)
        self._globalUnionFind = UnionFind()
        self._finalized = np.zeros(bs, dtype=np.bool)
        self._ccComputed = np.zeros(bs, dtype=np.bool)
        self._cc = np.empty(self.Input.meta.shape, dtype=labelType)
        self._result = np.empty(self.Input.meta.shape, dtype=labelType)

    def execute(self, slot, subindex, roi, result):
        assert slot == self.Output
        bg = self.Background.value
        #data = self.Input.get(roi).wait()
        #vigra.analysis.labelVolumeWithBackground(
        #    data, background_value=bg, out=result)
        neededBlocks = self._blocksFromRoi(roi)
        for block in neededBlocks:
            self._finalize(block)
        result[:] = self._result[roi.toSlice()]
        return result

    def propagateDirty(self, slot, subindex, roi):
        self.Output.setDirty(slice(None))

    def _calcBlockShape(self):
        bs = np.asarray([0, 0, 0])
        inshape = self.Input.meta.shape
        blockShape = self.BlockShape.value
        for i in range(3):
            a = int(blockShape[i])
            A = int(inshape[i])
            assert a <= A
            bs[i] = A/a + (1 if A%a else 0)

        return tuple(bs)

    def _roiFromBlock(self, block):
        block = np.asarray(block, dtype=np.int)
        inshape = self.Input.meta.shape
        blockShape = self.BlockShape.value
        start = np.asarray(blockShape, dtype=np.int)
        stop = np.asarray(blockShape, dtype=np.int)
        start = start * block
        stop = stop * (block+1)
        stop = np.where(stop > inshape, inshape, stop)
        roi = SubRegion(self.Input, start=start, stop=stop)
        return roi

    def _blocksFromRoi(self, roi):
        start = np.asarray(roi.start, dtype=np.int)
        stop = np.asarray(roi.stop, dtype=np.int)
        blockShape = np.asarray(self.BlockShape.value, dtype=np.int)

        start = start/blockShape
        rem = stop % blockShape
        stop = stop/blockShape
        out = [0, 0, 0]

        for i in range(3):
            stop[i] += (1 if rem[i] else 0)
            out[i] = np.arange(start[i], stop[i])
        X, Y, Z = np.meshgrid(out[0], out[1], out[2])
        
        out = [(x,y,z) for x, y, z in zip(X.flat, Y.flat, Z.flat)]
        
        return out

    def _getRegion(self, roi):
        blocks = [block for block in self._blocksFromRoi(roi) if not self._ccComputed[block]]
        for block in blocks:
            subroi = self._roiFromBlock(block)
            vigra.analysis.labelVolumeWithBackground(self.Input.get(subroi).wait(),
                                                     out=self._cc[subroi.toSlice()])
            self._ccComputed[block]
        return self._cc[roi.toSlice()]

    def _getNeighbours(self, block, nonFinal=False):
        bs = self._calcBlockShape()
        out = []
        for i in range(3):
            if block[i] > 0:
                s = np.asarray(block)
                s[i] -= 1
                out.append(tuple(s))
            if block[i] < bs[i]-1:
                s = np.asarray(block)
                s[i] += 1
                out.append(tuple(s))
        
        if nonFinal:
            out = [b for b in out if not self._finalized[b]]
        return out
    
    def _getFringe(self, a, b):
        roia = self._roiFromBlock(a)
        roib = self._roiFromBlock(b)
        
        for i in range(3):
            if a[i] < b[i]:
                start = np.asarray(roia.start)
                stop = np.asarray(roia.stop)
                start[i] = stop[i]-1
                newroia = SubRegion(self.Input, start=start, stop=stop)
                start = np.asarray(roib.start)
                stop = np.asarray(roib.stop)
                stop[i] = start[i]+1
                newroib = SubRegion(self.Input, start=start, stop=stop)
                return (self._getRegion(newroia).flat,
                        self._getRegion(newroib).flat)
            elif a[i] > b[i]:
                start = np.asarray(roia.start)
                stop = np.asarray(roia.stop)
                stop[i] = start[i]+1
                newroia = SubRegion(self.Input, start=start, stop=stop)
                start = np.asarray(roib.start)
                stop = np.asarray(roib.stop)
                start[i] = stop[i]-1
                newroib = SubRegion(self.Input, start=start, stop=stop)
                return (self._getRegion(newroia).flat,
                        self._getRegion(newroib).flat)
                
        assert False, "Must not get here!"

    def _finalize(self, block, labels=None):
        roi = self._roiFromBlock(block)
        vol = self._getRegion(roi)
        
        # initialize UnionFind
        if self._localUnionFinds[block] is None:
            self._localUnionFinds[block] = UnionFind(vol)
        
        # do makeUnion with neighbours
        neighbours = self._getNeighbours(block, nonFinal=True)
        for neighbour in neighbours:
            self._makeUnion(block, neighbour)
        
        # store result
        #self._localUnionFinds[block].compress()
        # local to global
        tempvol = self._localUnionFinds[block].mapArray(vol)
        # global relabeling
        self._result[roi.toSlice()] = self._globalUnionFind.mapArray(tempvol)
        self._finalized[block] = True

    def _makeUnion(self, blocka, blockb):
        a, b = self._getFringe(blocka, blockb)
        ufa = self._localUnionFinds[blocka]
        if self._localUnionFinds[blockb] is None:
            vol = self._getRegion(self._roiFromBlock(blockb))
            self._localUnionFinds[blockb] = UnionFind(vol)
        ufb = self._localUnionFinds[blockb]
        ufg = self._globalUnionFind

        idx = np.logical_and(a>0, b>0)
        a = a[idx]
        b = b[idx]
        visited = []
        for x, y in zip(a, b):
            if x in visited:
                continue
            else:
                visited.append(x)
            la, lb = ufa.realLabel(x), ufb.realLabel(y)
            if ufa.isGlobal(x):
                # use label x
                if ufb.isGlobal(y):
                    if la < lb:
                        globalLabel = la
                        ufg.relabel(lb, la)
                    elif x < y:
                        globalLabel = lb
                        ufg.relabel(la, lb)
                    else:
                        continue
                else:
                    globalLabel = la
            elif ufb.isGlobal(y):
                globalLabel = y
            else:
                globalLabel = ufg.getNewLabel()

            ufa.relabel(x, globalLabel)
            ufb.relabel(y, globalLabel)
            ufa.setGlobal(x)
            ufb.setGlobal(y)
        
        # set all remaining labels to final
        for k in [k for k in ufa.keys() if not ufa.isGlobal(k)]:
            ufa.relabel(k, ufg.getNewLabel())
            ufa.setGlobal(k)
            ufa.setFinal(k)


class UnionFind(object):
    def __init__(self, vol=None):
        labels = np.unique(vol) if vol is not None else (0,)
        # vigra does not support tuple(array)
        localLabels = [labels[i] for i in range(len(labels))]
        self._global = dict(zip(localLabels, (False,)*len(localLabels)))
        self._map = dict(zip(localLabels, localLabels))
        self._final = dict(zip(localLabels, (False,)*len(localLabels)))
        self._global[0] = True
        self._final[0] = True

    def isGlobal(self, x):
        return self._global[x]

    def realLabel(self, x):
        return self._map[x]

    def isFinal(self, x):
        return self._final[x]

    def getNewLabel(self):
        n = len(self._map)
        m = np.min(np.setdiff1d(np.arange(1, len(self._map)+1), self._map.keys()))
        self._map[m] = m
        self._final[m] = False
        self._global[m] = False
        return m

    def relabel(self, x, y):
        self._map[x] = y

    def setGlobal(self, x):
        self._global[x] = True

    def setFinal(self, x):
        self._final[x] = True

    def __getitem__(self, i):
        return self._map[i]

    def __setitem__(self, i, x):
        self.relabel(i, x)

    def keys(self):
        return self._map.keys()

    def mapArray(self, arr):
        labels = np.arange(np.max(self._map.keys())+1)
        for k in self._map:
            labels[k] = self._map[k]
        return labels[arr]






