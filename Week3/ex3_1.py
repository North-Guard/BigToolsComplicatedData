import numpy as np

# import data from matrix-file (Use your individual file location)
with open('matrix-file', 'r') as file:
    # split file into lines, split the lines into numbers at the comma delimiter, 
    #convert string number into int numbers
    num_list = [[int(num) for num in line.split()[0].split(',')] \
    			for line in file.readlines()]

# convert list of list of strings into a numpy array
M = np.asarray(num_list)
#Assigning all columns except the last one to A
A = M[:, :-1]
#Assigning only the last column to b
b = M[:, -1]
#Using the numpy linalg solve function to calculate x, given A and b from the matrix-file
x = np.linalg.solve(A, b)

# sanity check, calculating the dot product of A and x and comparing it to b
print('Ax = ', np.dot(A, x), ' b = ', b)
