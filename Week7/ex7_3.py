from mrjob.job import MRJob
from mrjob.step import MRStep

# Task, list all the bigrams in the shakespeare.txt 
# file, and the number of occurences
# This could be done without overriding "steps"

class MRmulti(MRJob):

    def mapper_get_bigrams(self, key, line):
        n = 0
        for word in line.split():
            if n > 0:
                yield "{} {}".format(prev_word, word), 1
            prev_word = word
            n += 1

    def sum_bigrams(self, bigram, values):
        yield sum(values), bigram

    def steps(self):
        return [MRStep(mapper=self.mapper_get_bigrams,
                       reducer=self.sum_bigrams)]

if __name__ == '__main__':
    MRmulti.run()


# Run like this
# python ex7_3.py shakespeare.txt | sort -n
