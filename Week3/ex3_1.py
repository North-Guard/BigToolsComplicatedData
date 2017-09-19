import numpy as np

# import data from file
with open('nparr', 'r') as file:
    # split file into lines, split the lines into numbers at the comma delimiter, convert string number into int numbers
    num_list = [[int(num) for num in line.split()[0].split(',')] for line in file.readlines()]

# convert list of list of strings into a numpy array
M = np.asarray(num_list)
A = M[:, :-1]
b = M[:, -1]

x = np.linalg.solve(A, b)

# sanity check
print('Ax = ', np.dot(A, x), ' b = ', b)
