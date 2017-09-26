from time import time

n = 10000
n_tests = 500

start = time()
for _ in range(n_tests):
    i = 1.0
    the_sum = 0.0
    while i <= n:
        the_sum += 1 / (i ** 2)
        i += 1
end = time()

print("Finished in time: {:.2f}s".format(end-start))
