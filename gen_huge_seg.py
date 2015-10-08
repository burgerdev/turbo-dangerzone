import numpy as np
import vigra

directory = '/home/burger/hci/hci-data/test/'

shape = (500, 500, 500)

vol = np.zeros(shape, dtype=np.uint8)
vol = vigra.taggedView(vol, axistags='zxy')

centers = [(45, 15), (45, 350), (360, 50)]
extent = (10, 10)
shift = (1, 1)
zrange = np.arange(0, 20)
zsteps = np.arange(5, 455, 50)

for x, y in centers:
    for z in zsteps:
        for t in zrange:
            sx = x+t*shift[0]
            sy = y+t*shift[1]
            vol[zsteps + t, sx-extent[0]:sx+extent[0], sy-extent[0]:sy+extent[0]] = 255

vol = vol.withAxes(*'xyz')
vigra.writeHDF5(vol, directory + 'huge_segmentation.h5', '/data', compression='gzip')
