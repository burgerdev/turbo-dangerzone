#!/usr/bin/python2

import vigra
import numpy as np

print("Testing for segfaults")

X = vigra.VigraArray(np.zeros((3,20,50)), axistags=vigra.defaultAxistags('zyx'))
labels = vigra.analysis.labelVolumeWithBackground(X)
print("np.zeros worked")

X = vigra.VigraArray(np.ones((3,20,50), dtype=np.uint8), axistags=vigra.defaultAxistags('xyz'))
labels = vigra.analysis.labelVolumeWithBackground(X)
print("XYZ (order=C) worked.")

X = vigra.VigraArray(np.ones((3,20,50), dtype=np.uint8), order='F', axistags=vigra.defaultAxistags('zyx'))
labels = vigra.analysis.labelVolumeWithBackground(X)
print("ZYX (order=F) worked.") 

X = vigra.VigraArray(np.ones((3,20,50), dtype=np.uint8), order='C', axistags=vigra.defaultAxistags('zyx'))
labels = vigra.analysis.labelVolume(X)
print("ZYX (order=C, labelVolume() )worked.") 



# this example fails with segmentation fault 
# Linux burger-Desktop 3.9.9-1-ARCH #1 SMP PREEMPT Wed Jul 3 22:45:16 CEST 2013 x86_64 GNU/Linux
# LIBS:
#       python2 2.7.5-1
#       boost-libs 1.54.0-2

X = vigra.VigraArray(np.ones((3,20,50), dtype=np.uint8), order='C', axistags=vigra.defaultAxistags('zyx'))
labels = vigra.analysis.labelVolumeWithBackground(X)
print("You fixed it.") 
