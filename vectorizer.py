from preprocess import PostgresCorpusReader
from nltk.text import TextCollection

class Vectorizer(object):
    def __init__(self):
        self.cr = PostgresCorpusReader()

    def one_hot(self):
        corpus = self.cr.tokenize()
        for desc in corpus:
            yield {
                token: True
                for sent in desc for token in sent
            }

    def tf_idf(self):
        corpus = [list(self.cr.tokenize_strip_punct(desc)) for desc in self.cr.texts()]
        texts = TextCollection(corpus)
        for desc in corpus:
            yield {
                term: texts.tf_idf(term, desc)
                for term in desc
            }