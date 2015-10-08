#!/usr/bin/python2

import numpy as np
import vigra
import psutil
#img  = vigra.impex.readImage("lena.png")[0:100,0:100]
#sp,nseg = vigra.analysis.slicSuperpixels(img,10, 10)
img = np.zeros((100, 100)).astype(np.float32)
sp = np.random.randint(10, size=img.shape).astype(np.uint32)

i=0
while True:
    i+=1
    if i%10 == 0:
        print psutil.phymem_usage()
    res = vigra.analysis.extractRegionFeatures(image=img, labels=sp)


