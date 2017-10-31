from mrjob.job import MRJob
from mrjob.step import MRStep

class MREuler(MRJob):


    # define the steps to take.
    # 1. get all the vertices
    # 2. count all the edges for each vertice
    # 3. split nodes into even or odd nodes
    # 4. count number of even and odd nodes
    def steps(self):
        return [MRStep(mapper=self.mapper_get_n_edges,
                       reducer=self.reducer_count_edges),
                MRStep(mapper=self.mapper_even_odd,
                       reducer=self.reducer_count_even_odd_vertices)]

    def mapper_get_n_edges(self, key, line):
        for elem in line.split():
            yield elem, 1

    def reducer_count_edges(self, vertice, edges):
        yield vertice, sum(edges)

    def mapper_even_odd(self, vertice, count):
        if count % 2 ==0:
            yield "# even nodes", 1
        else:
            yield "# odd nodes", 1

    def reducer_count_even_odd_vertices(self, key, values):
        yield key, sum(values)


if __name__ == "__main__":
    MREuler.run()



