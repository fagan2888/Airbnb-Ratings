#!/usr/bin/env python

#adapted from https://github.com/foxbook/atap/blob/master/snippets/ch02/reader.py

from nltk import sent_tokenize
import os
import psycopg2
import urllib.parse as up

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


if __name__ == '__main__':
    print('doing some preprocessing!')