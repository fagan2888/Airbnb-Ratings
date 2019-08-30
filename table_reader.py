#!/usr/bin/env python

# adapted from https://github.com/foxbook/atap/blob/master/snippets/ch02/reader.py
import psycopg2
import urllib.parse as up
import pandas.io.sql as sqlio
import pandas as pd
import json

def parse_amenities(amenities):
    drop_last = amenities[len(amenities) - 1] != '}'
    am_list = amenities[1:len(amenities)].split(',')
    if drop_last:
        del am_list[-1]
    else:
        am_list[-1] = am_list[-1][0:-1]
    return am_list


class TableReader(object):
    def __init__(self):
        up.uses_netloc.append("postgres")

        with open('config.json') as json_data_file:
            url = json.load(json_data_file)['database_url']

        url = up.urlparse(url)

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
        return props

    def properties_vector(self, include_amenitites = False):
        pv = self.properties()
        # we consider these high-priced properties "luxury" outliers
        pv = pv[pv['price'] < 400]
        # square_feet is mostly null, bed_type is 99.9% real bead
        pv = pv.drop(columns=['square_feet', 'bed_type'])
        # encode these columns
        for col in ['property_type', 'room_type']:
            dummies = pd.get_dummies(pv[col]);
            for dummy_col in dummies.columns:
                if dummies[dummy_col].sum() > 100:
                    pv[dummy_col] = dummies[dummy_col]
            pv = pv.drop(columns=[col])
         #fill in NaN/null
        for col in ['bathrooms', 'bedrooms', 'beds']:
            pv[col].fillna(pv[col].mean(), inplace=True)

        # one-hot encode amenities column
        if include_amenitites:
            new_columns = set()
            for index, row in pv.iterrows():
                for amenity in parse_amenities(row['amenities']):
                    if len(amenity) > 0:
                        new_columns.add(amenity)

            #make a dict with lists of 0/1 encodings
            amenities_dict = { key : list() for key in new_columns }
            for index, row in pv.iterrows():
                row_amenities = parse_amenities(row['amenities'])
                for col in new_columns:
                    if col in row_amenities and col in amenities_dict.keys():
                        amenities_dict[col].append(1)
                    else:
                        amenities_dict[col].append(0)

            #iterate over dic, make a columns for each key, assign array value
            for key, value in amenities_dict.items():
                if sum(value) > 100:
                    pv[key] = value;
            pv = pv.drop(columns=['amenities'])
        else:
            pv = pv.drop(columns=['amenities'])

        return pv

    def descriptions(self):
        sql = 'SELECT "listingID", name, summary, space, description, neighborhood_overview, notes, transit, access, interaction, house_rules FROM public."Descriptions";'
        descs = sqlio.read_sql_query(sql, self.conn)
        return descs

    def geodata(self):
        sql = 'SELECT "listingID", street, neighborhood, city, state, zipcode, smart_location, country, latitude, longitude FROM public."GeoData";'
        geo = sqlio.read_sql_query(sql, self.conn)
        return geo

    def geodata_vector(self):
        gv = self.geodata()
        # all these columns are 99% the same value
        gv = gv.drop(columns=['street', 'city', 'state', 'smart_location', 'country'])
        dummies = pd.get_dummies(gv['neighborhood']);
        for dummy_col in dummies.columns:
            if dummies[dummy_col].sum() > 100:
                gv[dummy_col] = dummies[dummy_col]
        gv = gv.drop(columns=['neighborhood'])
        gv['zipcode'].fillna(gv['zipcode'].mean(), inplace=True)
        return gv

    def reviews(self):
        sql = 'SELECT "listingID", num_reviews, rating, accuracy, cleanliness, checkin, communication, location, value FROM public."Reviews";'
        revs = sqlio.read_sql_query(sql, self.conn)
        return revs

    def reviews_vector(self):
        rv = self.reviews()
        for col in ['rating', 'accuracy', 'cleanliness', 'checkin', 'communication', 'location', 'value']:
            rv[col].fillna(rv[col].mean(), inplace=True)
        min_rating = 85
        rv['rating'] = rv['rating'].where(rv['rating'] >= min_rating, min_rating)
        return rv

    def close(self):
        self._cur.close()
        self.conn = None


if __name__ == '__main__':
    rdr = TableReader()
    df = rdr.properties_vector(True)
    print(df.head())
    rdr.close()
