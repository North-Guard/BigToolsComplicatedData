from time import time


bits_dict = {1: [[0], [1]]}


def bits(n):
    # This if function checks if the value of n is in the dictionary already
    if n in bits_dict:
        # This returns the object saved in the dictionary by the n-value.
        return bits_dict[n]
    else:
        li = bits(n - 1)
        l_all = []
        for i in range(len(li)):
            l0 = []
            l1 = []
            l0.extend(li[i])
            l0.extend([0])
            l1.extend(li[i])
            l1.extend([1])
            l_all.append(l0)
            l_all.append(l1)

            bits_dict[n] = l_all

        return bits_dict[n]


N = 22
start = time()
s = bits(N)
end = time()

print("Sequences created : {}".format(len(s)))
print("Sequences expected: {}".format(2**N))
print("Time for creation: {:.2f}s".format(end-start))
