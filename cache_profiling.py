#!/usr/bin/python

from pprint import pprint

import numpy as np
import vigra

from lazyflow.operators import OpCompressedCache, OpArrayCache, OpArrayPiper
from lazyflow.graph import Graph

from pympler.asizeof import asizeof, refs
from pympler.classtracker import ClassTracker

if __name__ == "__main__":

    tracker = ClassTracker()
    tracker.track_class(OpArrayCache, resolution_level=2)
    
    tracker.track_class(OpCompressedCache, resolution_level=2)

    g = Graph()
    vol = np.random.randint(255, size=(1000,1000,10)).astype(np.uint8)
    vol = vigra.taggedView(vol, axistags='xyz')
    
    pipe = OpArrayPiper(graph=g)
    pipe.Input.setValue(vol)
    
    cache1 = OpArrayCache(graph=g)
    tracker.track_object(vol)
    tracker.create_snapshot()
    cache1.Input.connect(pipe.Output)
    tracker.create_snapshot()
    
    cache2 = OpCompressedCache(graph=g)
    cache2.Input.connect(cache1.Output)
    tracker.create_snapshot()
    cache2.BlockShape.setValue((100,100,1))
    
    tracker.track_object(cache2._cacheFiles)
    #tracker.track_object(cache1)
    #tracker.track_object(cache2)
    
    '''
    print("Size of graph (before): {}".format(asizeof(g)))
    print("Size of array piper (before): {}".format(asizeof(pipe)))
    print("Size of uncompressed cache (before): {}".format(asizeof(cache1)))
    print("Size of compressed cache (before): {}".format(asizeof(cache2)))
    '''
    
    tracker.create_snapshot()
    
    vol2 = cache2.Output[...].wait()
    
    tracker.create_snapshot()
    
    '''
    print("Size of graph (after): {}".format(asizeof(g)))
    print("Size of array piper (after): {}".format(asizeof(pipe)))
    print("Size of uncompressed cache (after): {}".format(asizeof(cache1)))
    print("Size of compressed cache (after): {}".format(asizeof(cache2)))
    '''
    
    #print("")
    #pprint([o for o in refs(cache2)])
    #print("")
    
    
    tracker.stats.print_summary()

