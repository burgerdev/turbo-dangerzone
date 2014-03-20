
from lazyflow.request import Request, RequestPool

from time import sleep, time

def f():
    sleep(1)


n = 5

usePool = False

t = time()
pool = RequestPool()

for i in range(5):
    req = Request(f)
    pool.add(req)
    
pool.wait()
print(time() - t)

t = time()
agg = []
for i in range(5):
    req = Request(f)
    req.submit()
    agg.append(req)
for i in range(5):
    agg[i].wait()
print(time() - t)

t = time()
agg = []
for i in range(5):
    req = Request(f)
    agg.append(req)
for i in range(5):
    agg[i].wait()
print(time() - t)