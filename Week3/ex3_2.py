import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root

# read file containing points
with open('points', 'r') as file:
    # split each line into two strings, convert each one to float
    points = [[float(x) for x in point.split(' ')] for point in file.readlines()]

# convert list of floats to np array
M = np.asarray(points)
# show the points
plt.plot(M[:, 0], M[:, 1], 'bo')


# ----------------------------------------- #
# fit 3rd degree polynomial
# ----------------------------------------- #
coeffs = np.polyfit(M[:, 0], M[:, 1], deg=3)

# ----------------------------------------- #
# define function to minimize
# ----------------------------------------- #


def f(x, coeff):
    y = [x**i * coeff[i] for i in range(len(coeff))]
    return sum(y)

# plot function on the interval [-20,20]
x = np.linspace(-20, 20, 100)
y = f(x, coeffs)
plt.plot(x, y)


# ----------------------------------------- #
# find the roots
# ----------------------------------------- #

# 3rd degree polynomial, so there may be
#   1 root or
#   1 saddle point root or
#   3 roots
# initial guess
x0 = [-10, 0.0, 10]
res = root(f, x0, coeffs)

for x in res.x:
    print("x = {0:3.2f}\t f(x) = {1:3.2f}".format(x, f(x, coeffs)))


