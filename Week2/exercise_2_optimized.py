from time import time
import matplotlib.pyplot as plt
import numpy as np
plt.close("all")


start = time()

# Load the data
with open('Week2/pizza-train.json', 'r') as file:
    lines = [line.split() for line in file.readlines()]

# Get request_text's
lines = [line[1:] for line in lines if line[0] == '"request_text":']
n_lines = len(lines)

# Find all distinct words in vocabulary
words = set()
idx = 0
for line in lines:
    text = line
    words.update(text)

# Make a word-list and mapping to indices
words = sorted(list(words))
word2idx = {word: idx for idx, word in enumerate(words)}
n_words = len(words)

# Bag-of-words list of lists
bow = [[0] * n_words for _ in range(n_lines)]
for line_nr, line in enumerate(lines):
    text = line
    bow_row = bow[line_nr]

    for word in text:
        ix = word2idx[word]
        bow_row[ix] = 1

end = time()

# Sanity check that we did it right
im = np.array(bow)
plt.imshow(im)
plt.show()

# Most popular word
s = sum(im)
max_ix = np.where(s == max(s))

print('Most popular word: ')
print(words[max_ix[0][0]])

print("Script time: {:.2f}s".format(end - start))
