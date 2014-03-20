import numpy as np
import vigra

directory = '/home/mdoering/hci/hci-data/'

shape = (50, 500, 500)

vol = np.zeros(shape, dtype=np.uint8)
vol = vigra.taggedView(vol, axistags='zxy')

centers = [(20, 20), (30, 200), (210, 30)]
extent = (10, 10)
shift = (1, 1)
zrange = np.arange(25, 35)

for x, y in centers:
    for t in zrange:
        sx = x+t*shift[0]
        sy = y+t*shift[1]
        vol[t, sx-extent[0]:sx+extent[0], sy-extent[0]:sy+extent[0]] = 255

pred = np.ones(shape+(3,), dtype=np.float32)*.1
pred += (np.random.random(pred.shape)-.5)*.1
pred = vigra.taggedView(pred, axistags='zxyc')

i = 0
for x, y in centers:
    i += 1
    for t in zrange:
        sx = x+t*shift[0]
        sy = y+t*shift[1]
        pred[t, sx-extent[0]:sx+extent[0], sy-extent[0]:sy+extent[0], i%2 +1] += .8

predNull = pred[..., 0]
predNull[np.logical_and(pred[..., 1] < .5, pred[..., 2] < .5)] += .8

vol = vol.withAxes(*'xyz')
pred = pred.withAxes(*'xyzc')
vigra.writeHDF5(vol, directory + 'data.h5', '/data')
vigra.writeHDF5(pred, directory + 'pred.h5', '/data')
