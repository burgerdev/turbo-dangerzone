import numpy as np
import vigra

directory = '/home/burger/hci/hci-data/'

shape = (10, 100, 120)

vol = np.zeros(shape, dtype=np.uint8)
vol = vigra.taggedView(vol, axistags='zxy')

centers = [(15, 15), (15, 70), (60, 30)]
extent = (10, 10)
shift = (1, 1)
zrange = np.arange(3, 7)

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


vol = vol.withAxes(*'xyzt')
pred = pred.withAxes(*'xyzct')

volflipped = np.flipud(vol)
predflipped = np.flipud(pred)

vol = np.concatenate((vol, volflipped), axis=3)
assert len(vol.shape) == 4
vol = vigra.taggedView(vol, axistags='xyzt')

pred = np.concatenate((pred, predflipped), axis=4)
assert len(pred.shape) == 5
pred = vigra.taggedView(pred, axistags='xyzct')

vigra.writeHDF5(vol, directory + 'data5d.h5', '/data')
vigra.writeHDF5(pred, directory + 'pred5d.h5', '/data')
