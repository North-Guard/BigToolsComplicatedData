from time import time

import pyximport
pyximport.install()

from ex3_compute_sum import compute_sum

n = 10000
n_tests = 500

start = time()
for _ in range(n_tests):
    the_sum = compute_sum(n)
end = time()
print("Finished in time: {:.2f}s".format(end-start))
