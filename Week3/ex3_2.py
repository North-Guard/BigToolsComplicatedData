import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root

# read list of points file
with open('list-of-points-file', 'r') as file:
    # split each line into two strings, convert each one to float
    points = [[float(x) for x in point.split(' ')] for point in file.readlines()]

# convert list of floats to np array
M = np.asarray(points)
# Plot the points
plt.plot(M[:, 0], M[:, 1], 'bo')

# Using the numpy polyfit function to fit the points
# to a 3rd degree polynomial function
coeffs = np.polyfit(M[:, 0], M[:, 1], deg=3)

# Defining the function that calculates y, given a point x 
# and the coefficient that were estimated by the polyfit function above
def f(x, coeff):
    y = [x**(i) * coeff[-(i+1)] for i in range(len(coeff))]
    return sum(y)

# plot function on the interval [-20,20]
x = np.linspace(-20, 20, 100)
#Calculate y by calling the function defined above
y = f(x, coeffs)
# Plot the results
plt.plot(x, y)

# find the roots
# 3rd degree polynomial, so there may be
#   1 root or 1 saddle point root or 3 roots
# creating an inital guess initial guess
x0 = [-10, 0.0, 10]
# calling the scipy optimize root function, which approximates the roots of the
# function f
res = root(f, x0, coeffs)

# Print the approximated roots of the function
for x in res.x:
    print("x = {0:6.4f}\t f(x) = {1:6.4f}".format(x, f(x, coeffs)))
