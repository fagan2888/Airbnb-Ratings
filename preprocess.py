#!/usr/bin/env python

# adapted from https://github.com/foxbook/atap/blob/master/snippets/ch02/reader.py

from nltk import sent_tokenize, wordpunct_tokenize, pos_tag, FreqDist, download
download('punkt')
download('averaged_perceptron_tagger')
import os
import psycopg2
import urllib.parse as up
import time


testdata = ['We love living in Columbia Heights. Our house is minutes by foot from loads of local restaurants and an easy metro ride to all the DC tourist sites. Our Airbnb space is a comfy, cozy suite on the third floor of our house. We live in the house, but the third floor is all yours. We like to give you to your privacy but are available as needed for questions and help. Welcome! Our Airbnb guest suite is the third floor of our charming Victorian home in Columbia Heights -- a bustling, revitalized historic Washington D.C. neighborhood with a wide variety of restaurants and shopping -- all just 15 minutes to the monuments and museums via the Columbia Heights or Georgia Ave metro stops, both just a few blocks away. Accommodations include one bedroom, one bath, and a large combined kitchenette/living room. Bedroom has queen-sized bed, desk, dresser and large closet. Living area is furnished with a futon and a couch, one of which can accommodate a third person. The en suite bathroom features a cla',
            'A spacious and cozy two-bedroom apartment in the heart of Shaw/Old City, just south of U St. Lots of great light and character. The backyard is my favorite room. The condo is a short walk to good restaurants, bars, coffee shops, CVS, ATMs (Wells Fargo), five solid music venues, a movie theater, and public transportation (two blocks to the Metro [Shaw/U Street and buses]. You cant get more convenient. Highlights:  -Spacious 2 bedroom apt with 2 full bathrooms (tub and shower in both).  - Tri-level condo in an old rowhouse  -Lots of natural light. -Big backyard, including a comfortable deck and charcoal grill.    -Convenient location near several cool bars (All Souls (8 and T); music venues including the 930 Club and The Howard Theater; and excellent restaurants from Ethiopian (Habesha!) to Italian (Dinos!), Czech (Bistro Bohem) and tasty burgers (DC9).    -2 blocks from metro [Green and Yellow lines; U Street/Cardozo or Shaw/Howard] -2 blocks from #63 and #64 Buses at intersection of ',
            "Stay in this stylish basement apartment located in Petworth, just north of the lively Columbia Heights/Adams Morgan area of the city and only 5 miles from the national museums downtown. If you are looking for a place that's clean and affordable to stay on your next visit to DC, you've found it! Completely renovated, fully furnished with modern furniture, flatscreen TV, cable, Wi-fi, washer/dryer, kitchenware, queen bed, this space is a unique home away from home. Fresh clean towels, pillow and bed linens are provided along with microwave, coffee maker, toaster, hair dryer, iron & ironing-board. On-street parking is also available in front of the property. Parking is non-zoned/unrestricted, so visitor pass not needed. Enjoy your own private entrance, a full private European-styled kitchen, large private bathroom, private living room, and office niche. Warm up near the fire pit in the backyard in the early spring and autumn months. Relax on the patio, throw your favorite meal on the gril"]

class PostgresCorpusReader(object):
    def __init__(self):
        up.uses_netloc.append("postgres")

        url = up.urlparse(os.environ["DATABASE_URL"])

        #conn = psycopg2.connect(database=url.path[1:],
        #                        user=url.username,
        #                        password=url.password,
        #                        host=url.hostname,
        #                        port=url.port
        #                        )

        #self._cur = conn.cursor()

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
        #self._cur.execute("SELECT description FROM descriptions")
        for text in testdata:
            yield text

    def sents(self):
        for desc in self.texts():
            for sentence in sent_tokenize(desc):
                yield sentence

    def words(self):
        for sentence in self.sents():
            for token in wordpunct_tokenize(sentence):
                yield token

    def tokenize(self):
        for desc in self.texts():
            yield [
                pos_tag(wordpunct_tokenize(sent))
                for sent in sent_tokenize(desc)
            ]

    def describe(self):
        started = time.time()
        counts = FreqDist()
        tokens = FreqDist()

        for word in self.words():
            counts['words'] += 1
            tokens[word] += 1

        return {
            'words': counts['words'],
            'vocab': len(tokens),
            'lexdiv': float(counts['words']) / float(len(tokens)),
            'secs': time.time() - started,
        }


if __name__ == '__main__':
    print('doing some preprocessing!')
    cr = PostgresCorpusReader()
    print(cr.describe())