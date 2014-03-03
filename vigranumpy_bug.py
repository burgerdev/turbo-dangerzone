
import numpy as np
import vigra


x = np.zeros((1,))

try:
    a = x[1]
except IndexError:
    pass

x = vigra.taggedView(x, axistags='x')

try:
    a = x[1]
except IndexError:
    pass


