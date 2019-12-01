from mrjob.job import MRJob
from mrjob.compat import jobconf_from_env
from mrjob.step import MRStep
import string 

class MRPrac2(MRJob):
    SORT_VALUES = True
    def mapper(self, _, line):
        for x in string.punctuation:
            line = line.replace(x,' ')
        for word in line.split():
            yield (word.lower(), jobconf_from_env('map.input.file')), 1
        yield ('.total.',jobconf_from_env('map.input.file')), len(line)
        yield ('.doc.',jobconf_from_env('map.input.file')), 1
                    
    def reducer(self, words, counts):
        if words[0] != '.doc.':
            yield words, sum(counts)
        if words[0] != '.total.':
            yield (words[0],'.totales.'), 1
        
    def reducer2(self, words, counts):
        yield None, (words, sum(counts))
    
    def reducer3(self, _, values):
        first_value=values.next()
        num_docs=first_value[1]
        totalapar = 0
        for (word,doc), num in values:
            if word != '.doc.' and doc != '.totales.':
                yield doc, (word, num, totalapar, num_docs)
            else:
                totalapar = num

    def reducer4(self,key,values):
        first1_value=values.next()
        totalpaldoc=first1_value[1]
        for (a, b, c, d) in values:
            yield (a, key), (b, c, d, totalpaldoc)

    def steps(self):
        return [
            MRStep(mapper = self.mapper,
                    reducer = self.reducer),
            MRStep(reducer = self.reducer2),
            MRStep(reducer = self.reducer3),
            MRStep(reducer = self.reducer4)
        ]
                
if __name__ == '__main__':
    MRPrac2.run()