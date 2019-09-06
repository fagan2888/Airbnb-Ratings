#!/usr/bin/env python
from __future__ import print_function, unicode_literals
# adapted from https://github.com/foxbook/atap/blob/master/snippets/ch02/reader.py
import psycopg2
import urllib.parse as up
import pandas.io.sql as sqlio
import pandas as pd
import json
import os
import regex
from pyfiglet import Figlet
from PyInquirer import prompt, style_from_dict, Token
from PyInquirer import Validator, ValidationError
import pickle

class NumberValidator(Validator):
    def validate(self, document):
        try:
            val  = int(document.text)
            if val < 0 or val > 20:
                raise ValueError()
        except ValueError:
            raise ValidationError(
                message='Please enter a non-negative integer',
                cursor_position=len(document.text))  # Move cursor to end

serie = pd.Series(
    {'accomodates': 0.0,
     'bathrooms': 0.0,
     'bedrooms': 0.0,
     'beds': 0.0,
     'Apartment': 0.0,
     'Condominium': 0.0,
     'Guest suite': 0.0,
     'House': 0.0,
     'Serviced apartment': 0.0,
     'Townhouse': 0.0,
     'Entire home/apt': 0.0,
     'Private room': 0.0,
     'Shared room': 0.0,
     'Private living room': 0.0,
     'Cable TV': 0.0,
     'Wifi': 0.0,
     'Free street parking': 0.0,
     'Dishes and silverware': 0.0,
     'Washer': 0.0,
     'Doorman': 0.0,
     'Laptop friendly workspace': 0.0,
     'Suitable for events': 0.0,
     'TV': 0.0,
     'Smoking allowed': 0.0,
     'Family/kid friendly': 0.0,
     'Host greets you': 0.0,
     'Pets live on this property': 0.0,
     'Breakfast': 0.0,
     'Smoke detector': 0.0,
     'Kitchen': 0.0,
     'Dishwasher': 0.0,
     'Safety card': 0.0,
     'Air conditioning': 0.0,
     'First aid kit': 0.0,
     'Internet': 0.0,
     'Buzzer/wireless intercom': 0.0,
     'Free parking on premises': 0.0,
     'Lock on bedroom door': 0.0,
     'Refrigerator': 0.0,
     'Private entrance': 0.0,
     'Keypad': 0.0,
     'Bed linens': 0.0,
     'Bathtub': 0.0,
     'Shampoo': 0.0,
     'Dryer': 0.0,
     'Pool': 0.0,
     'Carbon monoxide detector': 0.0,
     'Dog(s)': 0.0,
     'Essentials': 0.0,
     'Iron': 0.0,
     'Hangers': 0.0,
     'Fire extinguisher': 0.0,
     'Pets allowed': 0.0,
     'Gym': 0.0,
     'Indoor fireplace': 0.0,
     'Hot tub': 0.0,
     'Coffee maker': 0.0,
     'Heating': 0.0,
     'Cat(s)': 0.0,
     'Self check-in': 0.0,
     'Wheelchair accessible': 0.0,
     'Extra pillows and blankets': 0.0,
     'Lockbox': 0.0,
     'translation missing: en.hosting_amenity_49': 0.0,
     'Other': 0.0,
     'Microwave': 0.0,
     '24-hour check-in': 0.0,
     'Hair dryer': 0.0,
     'Paid parking off premises': 0.0,
     'Hot water': 0.0,
     'translation missing: en.hosting_amenity_50': 0.0,
     'Elevator': 0.0,
     'Smart lock': 0.0,
     'Oven': 0.0,
     'Brightwood Park, Crestwood, Petworth': 0.0,
     'Brookland, Brentwood, Langdon': 0.0,
     'Capitol Hill, Lincoln Park': 0.0,
     'Capitol View, Marshall Heights, Benning Heights': 0.0,
     'Cathedral Heights, McLean Gardens, Glover Park': 0.0,
     'Cleveland Park, Woodley Park, Massachusetts Avenue Heights, Woodland-Normanstone Terrace': 0.0,
     'Columbia Heights, Mt. Pleasant, Pleasant Plains, Park View': 0.0,
     'Congress Heights, Bellevue, Washington Highlands': 0.0,
     'Downtown, Chinatown, Penn Quarters, Mount Vernon Square, North Capitol Street': 0.0,
     'Dupont Circle, Connecticut Avenue/K Street': 0.0,
     'Edgewood, Bloomingdale, Truxton Circle, Eckington': 0.0,
     'Friendship Heights, American University Park, Tenleytown': 0.0,
     'Georgetown, Burleith/Hillandale': 0.0,
     'Howard University, Le Droit Park, Cardozo/Shaw': 0.0,
     'Ivy City, Arboretum, Trinidad, Carver Langston': 0.0,
     'Kalorama Heights, Adams Morgan, Lanier Heights': 0.0,
     'Lamont Riggs, Queens Chapel, Fort Totten, Pleasant Hill': 0.0,
     'Near Southeast, Navy Yard': 0.0,
     'North Cleveland Park, Forest Hills, Van Ness': 0.0,
     'North Michigan Park, Michigan Park, University Heights': 0.0,
     'Shaw, Logan Circle': 0.0,
     'Southwest Employment Area, Southwest/Waterfront, Fort McNair, Buzzard Point': 0.0,
     'Spring Valley, Palisades, Wesley Heights, Foxhall Crescent, Foxhall Village, Georgetown Reservoir': 0.0,
     'Takoma, Brightwood, Manor Park': 0.0,
     'Twining, Fairlawn, Randle Highlands, Penn Branch, Fort Davis Park, Fort Dupont': 0.0,
     'Union Station, Stanton Park, Kingman Park': 0.0,
     'West End, Foggy Bottom, GWU': 0.0,
     'Woodridge, Fort Lincoln, Gateway': 0.0}
)

questions = [
    {
        'type': 'input',
        'name': 'accomodates',
        'message': 'How many people does your property accommodate?',
        'validate': NumberValidator
    },
    {
        'type': 'input',
        'name': 'bathrooms',
        'message': 'How many bathrooms does your property have?',
        'validate': NumberValidator
    },
    {
        'type': 'input',
        'name': 'bedrooms',
        'message': 'And bedrooms?',
        'validate': NumberValidator
    },
    {
        'type': 'input',
        'name': 'beds',
        'message': 'And how many beds will you provide?',
        'validate': NumberValidator
    },
    {
        'type': 'list',
        'name': 'prop_type',
        'message': 'Which term best describes your property?',
        'choices': ['Apartment', 'Condominium', 'Guest suite', 'House', 'Serviced apartment', 'Townhouse'],
    },
    {
        'type': 'list',
        'name': 'room_type',
        'message': 'And what kind of room are you offering?',
        'choices': ['Entire home/apt', 'Private room', 'Shared room'],
    },
    {
        'type': 'checkbox',
        'qmark': '?',
        'message': 'Select all amenities offered at your property.',
        'name': 'amenities',
        'choices': [
            {
                'name': 'Self check-in'
            },
            {
                'name': 'Paid parking off premises'
            },
            {
                'name': 'Dryer'
            },
            {
                'name': 'Lockbox',
            },
            {
                'name': 'Cat(s)'
            },
            {
                'name': 'Pets live on this property'
            },
            {
                'name': 'Oven'
            },
            {
                'name': 'Shampoo'
            },
            {
                'name': 'TV'
            },
            {
                'name': 'Family/kid friendly'
            },
            {
                'name': 'Elevator',
            },
            {
                'name': 'Hair dryer'
            },
            {
                'name': 'Hangers',
            },
            {
                'name': 'Hot water',
            },
            {
                'name': 'Smoking allowed',
            },
            {
                'name': 'Iron',
            },
            {
                'name': 'Gym',
            },
            {
                'name': 'Dog(s)',
            },
            {
                'name': 'Smoke detector',
            },
            {
                'name': 'Other',
            },
            {
                'name': 'Pets allowed',
            },
            {
                'name': 'Free street parking',
            },
            {
                'name': 'Refrigerator',
            },
            {
                'name': 'Private living room',
            },
            {
                'name': 'Fire extinguisher',
            },
            {
                'name': 'Bed linens',
            },
            {
                'name': 'Internet',
            },
            {
                'name': 'Carbon monoxide detector',
            },
            {
                'name': 'Laptop friendly workspace',
            },
            {
                'name': 'Microwave',
            },
            {
                'name': 'Extra pillows and blankets',
            },
            {
                'name': 'Dishwasher',
            },
            {
                'name': 'Hot tub',
            },
            {
                'name': 'Lock on bedroom door',
            },
            {
                'name': 'Free parking on premises',
            },
            {
                'name': 'Doorman',
            },
            {
                'name': 'Pool',
            },
            {
                'name': 'Wheelchair accessible',
            },
            {
                'name': 'Suitable for events',
            },
            {
                'name': 'Essentials',
            },
            {
                'name': 'Breakfast',
            },
            {
                'name': 'Washer',
            },
            {
                'name': 'Keypad',
            },
            {
                'name': 'First aid kit',
            },
            {
                'name': 'Private entrance',
            },
            {
                'name': 'Host greets you',
            },
            {
                'name': 'Kitchen',
            },
            {
                'name': 'Dishes and silverware',
            },
            {
                'name': 'Coffee maker',
            },
            {
                'name': '24-hour check-in',
            },
            {
                'name': 'Heating',
            },
            {
                'name': 'Air conditioning',
            },
            {
                'name': 'Bathtub',
            },
            {
                'name': 'Wifi',
            },
            {
                'name': 'Indoor fireplace',
            },
        ],
    },
    {
        'type': 'list',
        'name': 'neighborhood',
        'message': 'Finally, what neighborhood is your property located in?',
        'choices': ["Brightwood Park, Crestwood, Petworth",
                    "Brookland, Brentwood, Langdon",
                    "Capitol Hill, Lincoln Park",
                    "Capitol View, Marshall Heights, Benning Heights",
                    "Cathedral Heights, McLean Gardens, Glover Park",
                    "Cleveland Park, Woodley Park, Massachusetts Avenue Heights, Woodland-Normanstone Terrace",
                    "Columbia Heights, Mt. Pleasant, Pleasant Plains, Park View",
                    "Congress Heights, Bellevue, Washington Highlands",
                    "Downtown, Chinatown, Penn Quarters, Mount Vernon Square, North Capitol Street",
                    "Dupont Circle, Connecticut Avenue/K Street",
                    "Edgewood, Bloomingdale, Truxton Circle, Eckington",
                    "Friendship Heights, American University Park, Tenleytown",
                    "Georgetown, Burleith/Hillandale",
                    "Howard University, Le Droit Park, Cardozo/Shaw",
                    "Ivy City, Arboretum, Trinidad, Carver Langston",
                    "Kalorama Heights, Adams Morgan, Lanier Heights",
                    "Lamont Riggs, Queens Chapel, Fort Totten, Pleasant Hill",
                    "Near Southeast, Navy Yard",
                    "North Cleveland Park, Forest Hills, Van Ness",
                    "North Michigan Park, Michigan Park, University Heights",
                    "Shaw, Logan Circle",
                    "Southwest Employment Area, Southwest/Waterfront, Fort McNair, Buzzard Point",
                    "Spring Valley, Palisades, Wesley Heights, Foxhall Crescent, Foxhall Village, Georgetown Reservoir",
                    "Takoma, Brightwood, Manor Park",
                    "Twining, Fairlawn, Randle Highlands, Penn Branch, Fort Davis Park, Fort Dupont",
                    "Union Station, Stanton Park, Kingman Park",
                    "West End, Foggy Bottom, GWU",
                    "Woodridge, Fort Lincoln, Gateway"],
    }
]

if __name__ == '__main__':
    f = Figlet(font='slant')
    print(f.renderText('Airbnb pricer'))
    answers = prompt(questions)
    for col in ['accomodates', 'bathrooms', 'bedrooms', 'beds']:
        serie[col] = answers[col]
    for q in ['prop_type', 'room_type', 'neighborhood']:
        serie[answers[q]] = 1.0
    for amenity in answers['amenities']:
        serie[amenity] = 1.0

    loaded_model = pickle.load(open('demo_model.sav', 'rb'))
    result = "{:.2f}".format(loaded_model.predict([serie])[0])
    result_f = Figlet(font='standard')
    print(result_f.renderText('Suggested price: $'+result))
