#!/usr/bin/env python

# adapted from https://github.com/foxbook/atap/blob/master/snippets/ch02/reader.py
import os
import psycopg2
import urllib.parse as up
import pandas as pd
import pandas.io.sql as sqlio


class TableReader(object):
    def __init__(self):
        up.uses_netloc.append("postgres")

        url = up.urlparse(os.environ["DATABASE_URL"])

        self.conn = psycopg2.connect(database=url.path[1:],
                                user=url.username,
                                password=url.password,
                                host=url.hostname,
                                port=url.port
                                )

        self._cur = self.conn.cursor()

    def ids(self):
        self._cur.execute('SELECT "listingID" FROM public."Properties"')
        for idx in iter(self._cur.fetchone, None):
            yield idx[0]

    def properties(self):
        sql = 'SELECT "listingID", property_type, room_type, accomodates, bathrooms, bedrooms, beds, bed_type, amenities, square_feet, price FROM public."Properties";'
        props = sqlio.read_sql_query(sql, self.conn)
        return props;

    def descriptions(self):
        sql = 'SELECT "listingID", name, summary, space, description, neighborhood_overview, notes, transit, access, interaction, house_rules FROM public."Descriptions";'
        descs = sqlio.read_sql_query(sql, self.conn)
        return descs;

    def geodata(self):
        sql = 'SELECT "listingID", street, neighborhood, city, state, zipcode, smart_location, country, latitude, longitude FROM public."GeoData";'
        geo = sqlio.read_sql_query(sql, self.conn)
        return geo;

    def reviews(self):
        sql = 'SELECT "listingID", num_reviews, rating, accuracy, cleanliness, checkin, communication, location, value FROM public."Reviews";'
        revs = sqlio.read_sql_query(sql, self.conn)
        return revs;

    def close(self):
        self._cur.close()
        self.conn = None


if __name__ == '__main__':
    rdr = TableReader()
    df = rdr.properties();
    print(df.head())
    rdr.close()
