import os
from re import template
import pandas as pd

import sys
sys.path.append('.')
from benchmarkUtils.database import DB


class Restaurant:
    def __init__(self, dbp) -> None:
        db = DB(dbp)
        self.tables = db.tables

        self.geographic = self.tables['geographic']
        self.generalinfo = self.tables['generalinfo']
        self.location = self.tables['location']

    def q0(self):
        template = 'Which street is {label} located in?'
        row = self.location.sample(1)
        id_restaurant = row['id_restaurant'].iloc[0]
        street_name = row['street_name'].iloc[0]
        label = self.generalinfo[self.generalinfo['id_restaurant'] == id_restaurant]['label'].iloc[0]
        question = template.format(label=label)
        return question, street_name

    def q1(self):
        template = 'Which county has the most {food_type} restaurant?'
        food_type = self.generalinfo['food_type'].sample(1).iloc[0]
        filted = self.generalinfo[self.generalinfo['food_type'] == food_type]
        filted = pd.merge(filted, self.geographic, how='left', left_on='city', right_on='city')
        max_count = filted['county'].value_counts()
        max_val = max_count.max()
        max_county = max_count[max_count == max_val].index.to_list()
        question = template.format(food_type=food_type)
        return question, max_county

    def q2(self):
        template = 'How many restaurants are reviewed more than {review:.2f}?'
        review = self.generalinfo['review'].sample(1).iloc[0] - 0.1
        filted = self.generalinfo[self.generalinfo['review'] > review]
        count = len(filted)
        question = template.format(review=review)
        return question, count

    def q3(self):
        template = 'What is the average review of {food_type} restaurants?'
        food_type = self.generalinfo['food_type'].sample(1).iloc[0]
        filted = self.generalinfo[self.generalinfo['food_type'] == food_type]
        avg = filted['review'].mean()
        question = template.format(food_type=food_type)
        return question, avg

    def q4(self):
        template = 'What is the total review of {food_type} restaurants?'
        food_type = self.generalinfo['food_type'].sample(1).iloc[0]
        filted = self.generalinfo[self.generalinfo['food_type'] == food_type]
        total = filted['review'].sum()
        question = template.format(food_type=food_type)
        return question, total

    def q5(self):
        template = 'Which county is {label} located in?'
        row = self.generalinfo.sample(1)
        label = row['label'].iloc[0]
        city = row['city'].iloc[0]
        county = self.geographic[self.geographic['city'] == city]['county'].iloc[0]
        question = template.format(label=label)
        return question, county

    def q6(self):
        template = 'In {county}, which food type restaurant is the most common?'
        county = self.geographic['county'].sample(1).iloc[0]
        cities = self.geographic[self.geographic['county'] == county]['city']
        filted = self.generalinfo[self.generalinfo['city'].isin(cities)]
        max_count = filted['food_type'].value_counts()
        max_val = max_count.max()
        food_type = max_count[max_count == max_val].index.to_list()
        question = template.format(county=county)
        return question, food_type

    def q7(self):
        template = 'How many restaurants are located in {county}?'
        county = self.geographic['county'].sample(1).iloc[0]
        cities = self.geographic[self.geographic['county'] == county]['city']
        filted = self.generalinfo[self.generalinfo['city'].isin(cities)]
        count = len(filted)
        question = template.format(county=county)
        return question, count

    def q8(self):
        template = 'What is the average review of restaurants in {county}?'
        county = self.geographic['county'].sample(1).iloc[0]
        cities = self.geographic[self.geographic['county'] == county]['city']
        filted = self.generalinfo[self.generalinfo['city'].isin(cities)]
        avg = filted['review'].mean()
        question = template.format(county=county)
        return question, avg

    def q9(self):
        template = 'What is the total review of restaurants in {county}?'
        county = self.geographic['county'].sample(1).iloc[0]
        cities = self.geographic[self.geographic['county'] == county]['city']
        filted = self.generalinfo[self.generalinfo['city'].isin(cities)]
        total = filted['review'].sum()
        question = template.format(county=county)
        return question, total


if __name__ == '__main__':
    dbRoot = 'dataset/optmizedScaledDB/8k/'
    dbn = 'restaurant'
    dbp = os.path.join(dbRoot, dbn, f'{dbn}.sqlite')
    fi = Restaurant(dbp)
    print(fi.q0())
    print(fi.q1())
    print(fi.q2())
    print(fi.q3())
    print(fi.q4())
    print(fi.q5())
    print(fi.q6())
    print(fi.q7())
    print(fi.q8())
    print(fi.q9())