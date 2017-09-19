from time import time


bits_dict = {1: [[0], [1]]}


def bits(n):
    if n not in bits_dict:
        l_all = [
            [val, *li]
            for val in [0, 1]
            for li in bits(n - 1)
        ]

        # Store subproblem result
        bits_dict[n] = l_all

    return bits_dict[n]


N = 22
start = time()
s = bits(N)
end = time()

print("Sequences created : {}".format(len(s)))
print("Sequences expected: {}".format(2**N))
print("Time for creation: {:.2f}s".format(end-start))
