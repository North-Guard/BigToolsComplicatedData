from time import time


def bits(N):
    if N == 1:
        return [[0], [1]]
    else:
        l = bits(N-1)
        l_all = []
        for i in range(len(l)):
            l0 = []
            l1 = []
            l0.extend(l[i])
            l0.extend([0])
            l1.extend(l[i])
            l1.extend([1])
            l_all.append(l0)
            l_all.append(l1)

        return l_all


N = 15
start = time()
s = bits(N)
end = time()

print("Sequences created : {}".format(len(s)))
print("Sequences expected: {}".format(2**N))
print("Time for creation: {:.2f}s".format(end-start))
