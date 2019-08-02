#!/usr/bin/env python

# adapted from https://github.com/foxbook/atap/blob/master/snippets/ch02/reader.py
import os
import psycopg2
import urllib.parse as up


class TableReader(object):
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
        self._cur.execute('SELECT "listingID" FROM public."Properties"')
        for idx in iter(self._cur.fetchone, None):
            yield idx[0]

    def properties(self):
        self._cur.execute(
            'SELECT "listingID", property_type, room_type, accomodates, bathrooms, bedrooms, beds, bed_type, amenities, square_feet, price FROM public."Properties"')
        for prop in iter(self._cur.fetchone, None):
            yield prop

    def descriptions(self):
        self._cur.execute(
            'SELECT "listingID", name, summary, space, description, neighborhood_overview, notes, transit, access, interaction, house_rules FROM public."Descriptions";')
        for desc in iter(self._cur.fetchone, None):
            yield desc

    def geodata(self):
        self._cur.execute(
            'SELECT "listingID", street, neighborhood, city, state, zipcode, smart_location, country, latitude, longitude FROM public."GeoData";')
        for geo in iter(self._cur.fetchone, None):
            yield geo

    def reviews(self):
        self._cur.execute(
            'SELECT "listingID", num_reviews, rating, accuracy, cleanliness, checkin, communication, location, value FROM public."Reviews";')
        for rev in iter(self._cur.fetchone, None):
            yield rev

    def close(self):
        self._cur.close()


if __name__ == '__main__':
    rdr = TableReader()
    for item in rdr.properties():
        print(item)
    rdr.close()
