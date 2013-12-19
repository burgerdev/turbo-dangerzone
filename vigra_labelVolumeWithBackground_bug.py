#!/usr/bin/python2

import numpy as np
import vigra

def failing_vigra_test():
	print(vigra.__version__.version)
	v = np.zeros((10,10,10), dtype=np.uint8)
	v[3:6,3:6,1:3] = 1
	v[8:10,8:10,6:8] = 1
	w = vigra.analysis.labelVolumeWithBackground(v)

	#print(v[...,6:8])
	#print(w[...,6:8])

	assert w[3,3,1]>0, "Should be labeled"
	assert w[8,8,6]>0, "Should also be labeled"


if __name__ == "__main__":
	failing_vigra_test()
