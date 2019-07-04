#!/usr/bin/env python

# adapted from https://github.com/foxbook/atap/blob/master/snippets/ch02/reader.py

from nltk import sent_tokenize, wordpunct_tokenize, pos_tag, FreqDist
import os
import psycopg2
import urllib.parse as up
import time


class PostgresCorpusReader(object):
    def __init__(self):
        up.uses_netloc.append("postgres")

        url = up.urlparse(os.environ["DATABASE_URL"])

        conn = psycopg2.connect(database=url.path[1:],
                                user=url.username,
                                password=url.password,
                                host=url.hostname,
                                port=url.port
                                )

        self._cur = conn.cursor()

    def ids(self):
        # todo amend to match real table
        self._cur.execute("SELECT scrape_id FROM descriptions")
        for idx in iter(self._cur.fetchone, None):
            yield idx

    def scores(self):
        # todo amend to match real table
        self._cur.execute("SELECT review_scores_rating from ratings")
        for score in iter(self._cur.fetchone, None):
            yield score

    def texts(self):
        # todo amend to match real table
        self._cur.execute("SELECT description FROM descriptions")
        for text in iter(self._cur.fetchone, None):
            yield text

    def sents(self, fileids=None, categories=None):
        for desc in self.texts(fileids, categories):
            for sentence in sent_tokenize(desc):
                yield sentence

    def words(self, fileids=None, categories=None):
        for sentence in self.sents(fileids, categories):
            for token in wordpunct_tokenize(sentence):
                yield token

    def tokenize(self, fileids=None, categories=None):
        for desc in self.texts(fileids, categories):
            yield [
                pos_tag(wordpunct_tokenize(sent))
                for sent in sent_tokenize(desc)
            ]

    def describe(self, fileids=None, categories=None):
        started = time.time()
        counts = FreqDist()
        tokens = FreqDist()

        for desc in self.texts(fileids, categories):
            counts['descs'] += 1
            for sent in desc:
                counts['sents'] += 1
                for word, tag in sent:
                    counts['words'] += 1
                    tokens[word] += 1

        n_fileids = len(self.resolve(fileids, categories) or self.fileids())
        n_topics = len(self.categories(self.resolve(fileids, categories)))

        return {
            'files': n_fileids,
            'topics': n_topics,
            'paras': counts['paras'],
            'sents': counts['sents'],
            'words': counts['words'],
            'vocab': len(tokens),
            'lexdiv': float(counts['words']) / float(len(tokens)),
            'ppdoc': float(counts['paras']) / float(n_fileids),
            'sppar': float(counts['sents']) / float(counts['paras']),
            'secs': time.time() - started,
        }


if __name__ == '__main__':
    print('doing some preprocessing!')