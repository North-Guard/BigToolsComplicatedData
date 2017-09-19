from time import time
import matplotlib.pyplot as plt
import numpy as np
plt.close("all")

start = time()

# load the data
fid = open('Week2/pizza-train.json', 'r')

# find all distinct words
words = []

for line in fid:
    l = line.split()
    if l[0] == '"request_text":':
        text = l[1:]

        for word in text:
            if word not in words:
                words.append(word)

fid.close()

n_words = len(words)

# reload the data and create the bag-of-words matrix  list of lists
fid = open('Week2/pizza-train.json', 'r')

bow = []  # bag-of-words list of lists

for line in fid:
    l = line.split()
    if l[0] == '"request_text":':
        text = l[1:]

        bow_row = [0] * n_words  # row for the bow list of length n_words
        for word in text:
            ix = words.index(word)  # index in the word list where the current word matches
            bow_row[ix] = 1

        bow.append(bow_row)


fid.close()

end = time()

# sanity check that we did it right
im = np.array(bow)

plt.imshow(im)
plt.show()

# most popular word
s = sum(im)
max_ix = np.where(s == max(s))
print('Most popular word: ')
print(words[max_ix[0][0]])

print("Script time:: {:.2f}s".format(end-start))
