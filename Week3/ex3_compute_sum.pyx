def compute_sum(n):
    cdef float the_sum = 0.0
    cdef float i = 1
    while i <= n:
        the_sum += 1.0 / i ** 2
        i += 1.0
    return the_sum
