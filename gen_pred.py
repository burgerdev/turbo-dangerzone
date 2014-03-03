import numpy as np
import vigra

shape = (50, 500, 500)

vol = np.zeros(shape, dtype=np.uint8)
vol = vigra.taggedView(vol, axistags='txy')

centers = [(20, 20), (30, 200), (210, 30)]
extent = (10, 10)
shift = (5, 5)

for x, y in centers:
    for t in range(shape[0]):
        sx = x+t*shift[0]
        sy = y+t*shift[1]
        vol[t, sx-extent[0]:sx+extent[0], sy-extent[0]:sy+extent[0]] = 255

pred = np.ones(shape+(2,), dtype=np.float32)*.1
pred += (np.random.random(shape+(2,))-.5)*.1
pred = vigra.taggedView(pred, axistags='txyc')

i = 0
for x, y in centers:
    i += 1
    for t in range(shape[0]):
        sx = x+t*shift[0]
        sy = y+t*shift[1]
        pred[t, sx-extent[0]:sx+extent[0], sy-extent[0]:sy+extent[0], i%2] += .8


vigra.writeHDF5(vol, '/home/burger/Private/Coding/hci/hci-data/test/data.h5', '/data')
vigra.writeHDF5(pred, '/home/burger/Private/Coding/hci/hci-data/test/pred.h5', '/data')
