import numpy as np

from lazyflow.utility.fastWhere import fastWhere

from timeit import timeit

if __name__ == "__main__":

    A = np.random.randint(0, 255, size=(500, 500, 50)).astype(np.uint8)
    B = np.random.randint(0, 255, size=(500, 500, 50)).astype(np.uint8)
    C = np.random.randint(0, 255, size=(500, 500, 50)).astype(np.uint8)


    print("NUMPY")
    print(timeit("np.where(A>0, B, C).astype(np.uint32)", setup="from __main__ import A, B, C, np", number=10))
    print("THORBEN")
    print(timeit("fastWhere(A>0, B, C, np.uint32)", setup="from __main__ import A, B, C, fastWhere, np", number=10))