import numpy as np, datetime


x = np.random.randint(0,255,size=(5000,400,30)).astype(np.uint8)

def thresh(a,t):
    return a>t
vthresh = np.vectorize(thresh)

t0 = datetime.datetime.now()
y = x>128
print datetime.datetime.now() - t0

t0 = datetime.datetime.now()
y = vthresh(x, 128)
print datetime.datetime.now() - t0


t0 = datetime.datetime.now()
y = np.where(x>128, 1, 0)
print datetime.datetime.now() - t0

t0 = datetime.datetime.now()
x[:] = (x>128)
print datetime.datetime.now() - t0


