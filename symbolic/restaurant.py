import os
from random import choices
from re import template
import pandas as pd

import sys
sys.path.append('.')
from benchmarkUtils.database import DB
from symbolic.utils import choiceGen, corrGen, stmtGen, numericalGen


class Restaurant:
    retrieval = [
        ['location', 'generalinfo'],
        ['generalinfo', 'geographic'],
        ['generalinfo'],
        ['generalinfo'],
        ['generalinfo'],
        ['generalinfo', 'geographic'],
        ['generalinfo', 'geographic'],
        ['generalinfo', 'geographic'],
        ['generalinfo', 'geographic'],
        ['generalinfo', 'geographic']
    ]
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

        rightIdx, choices = choiceGen(street_name, self.location['street_name'])
        stmts = stmtGen(choices,
                        '{label} located in <unk>.'.format(label=label))
        return question, street_name, rightIdx, choices, stmts

    def q1(self):
        template = 'Which county has the most {food_type} restaurant?'
        food_type = self.generalinfo['food_type'].sample(1).iloc[0]
        filted = self.generalinfo[self.generalinfo['food_type'] == food_type]
        filted = pd.merge(filted, self.geographic, how='left', left_on='city', right_on='city')
        max_count = filted['county'].value_counts()
        max_val = max_count.max()
        max_county = max_count[max_count == max_val].index.to_list()
        question = template.format(food_type=food_type)

        rightIdx, choices = choiceGen(max_county, self.geographic['county'])
        stmts = stmtGen(choices,
                        'The <unk> county has the most {food_type} restaurant.'.format(food_type=food_type))
        return question, max_county, rightIdx, choices, stmts

    def q2(self):
        template = 'How many restaurants are reviewed more than {review:.2f}?'
        review = self.generalinfo['review'].sample(1).iloc[0] - 0.1
        filted = self.generalinfo[self.generalinfo['review'] > review]
        count = len(filted)
        question = template.format(review=review)

        rightIdx, choices = numericalGen(count)
        stmts = stmtGen(choices,
                        'There are <unk> restaurants are reviewed more than {review:.2f}.'.format(review=review))
        return question, count, rightIdx, choices, stmts

    def q3(self):
        template = 'What is the average review of {food_type} restaurants?'
        food_type = self.generalinfo['food_type'].sample(1).iloc[0]
        filted = self.generalinfo[self.generalinfo['food_type'] == food_type]
        avg = filted['review'].mean()
        question = template.format(food_type=food_type)

        rightIdx, choices = numericalGen(avg)
        stmts = stmtGen(choices,
                        'The average review of {food_type} restaurants is <unk>.'.format(food_type=food_type))
        return question, avg, rightIdx, choices, stmts

    def q4(self):
        template = 'What is the total review of {food_type} restaurants?'
        food_type = self.generalinfo['food_type'].sample(1).iloc[0]
        filted = self.generalinfo[self.generalinfo['food_type'] == food_type]
        total = filted['review'].sum()
        question = template.format(food_type=food_type)

        rightIdx, choices = numericalGen(total)
        stmts = stmtGen(choices,
                        'The total review of {food_type} restaurants is <unk>'.format(food_type=food_type))
        return question, total, rightIdx, choices, stmts

    def q5(self):
        template = 'Which county is {label} located in?'
        row = self.generalinfo.sample(1)
        label = row['label'].iloc[0]
        city = row['city'].iloc[0]
        county = self.geographic[self.geographic['city'] == city]['county'].iloc[0]
        question = template.format(label=label)

        rightIdx, choices = choiceGen(county, self.geographic['county'])
        stmts = stmtGen(choices,
                        '{label} is located in <unk>.'.format(label=label))
        return question, county, rightIdx, choices, stmts

    def q6(self):
        template = 'In {county}, which food type restaurant is the most common?'
        county = self.geographic['county'].sample(1).iloc[0]
        cities = self.geographic[self.geographic['county'] == county]['city']
        filted = self.generalinfo[self.generalinfo['city'].isin(cities)]
        max_count = filted['food_type'].value_counts()
        max_val = max_count.max()
        food_type = max_count[max_count == max_val].index.to_list()
        question = template.format(county=county)

        rightIdx, choices = choiceGen(food_type, self.generalinfo['food_type'])
        stmts = stmtGen(choices,
                        'In {county}, the <unk> restaurant is the most common.'.format(county=county))
        return question, food_type, rightIdx, choices, stmts

    def q7(self):
        template = 'How many restaurants are located in {county}?'
        county = self.geographic['county'].sample(1).iloc[0]
        cities = self.geographic[self.geographic['county'] == county]['city']
        filted = self.generalinfo[self.generalinfo['city'].isin(cities)]
        count = len(filted)
        question = template.format(county=county)

        rightIdx, choices = numericalGen(count)
        stmts = stmtGen(choices,
                        'There are <unk> restaurants are located in {county}.'.format(county=county))
        return question, count, rightIdx, choices, stmts

    def q8(self):
        template = 'What is the average review of restaurants in {county}?'
        county = self.geographic['county'].sample(1).iloc[0]
        cities = self.geographic[self.geographic['county'] == county]['city']
        filted = self.generalinfo[self.generalinfo['city'].isin(cities)]
        avg = filted['review'].mean()
        question = template.format(county=county)

        rightIdx, choices = numericalGen(avg)
        stmts = stmtGen(choices,
                        'The average review of restaurants in {county} is <unk>.'.format(county=county))
        return question, avg, rightIdx, choices, stmts

    def q9(self):
        template = 'What is the total review of restaurants in {county}?'
        county = self.geographic['county'].sample(1).iloc[0]
        cities = self.geographic[self.geographic['county'] == county]['city']
        filted = self.generalinfo[self.generalinfo['city'].isin(cities)]
        total = filted['review'].sum()
        question = template.format(county=county)

        rightIdx, choices = numericalGen(total)
        stmts = stmtGen(choices,
                        'The total review of restaurants in {county} is <unk>.'.format(county=county))
        return question, total, rightIdx, choices, stmts

    def q10(self):
        template = 'How many review scores are {label0} more than {label1}?'
        rows = self.generalinfo.sample(2)
        label0 = rows['label'].iloc[0]
        label1 = rows['label'].iloc[1]
        diff = rows['review'].iloc[0] - rows['review'].iloc[1]
        question = template.format(label0=label0, label1=label1)

        rightIdx, choices = numericalGen(diff)
        return question, diff, rightIdx, choices

    def q11(self):
        template = 'How many average review scores are food type {food_type0} more than {food_type1}?'
        food_types = self.generalinfo['food_type'].drop_duplicates().sample(2)
        food_type0 = food_types.iloc[0]
        food_type1 = food_types.iloc[1]
        diff = self.generalinfo[self.generalinfo['food_type'] == food_type0]['review'].mean() - self.generalinfo[self.generalinfo['food_type'] == food_type1]['review'].mean()
        question = template.format(food_type0=food_type0, food_type1=food_type1)

        rightIdx, choices = numericalGen(diff)
        return question, diff, rightIdx, choices

    def q12(self):
        template = 'What is the correlation between restaurant id and street num of restaurants that are {food_type} type?'
        food_type = self.generalinfo['food_type'].sample(1).iloc[0]
        ids = self.generalinfo[self.generalinfo['food_type'] == food_type]['id_restaurant']
        filted = self.location[self.location['id_restaurant'].isin(ids)]
        corr = filted['id_restaurant'].corr(filted['street_num'])
        question = template.format(food_type=food_type)

        rightIdx, choices = corrGen(corr)
        return question, corr, rightIdx, choices

    def q13(self):
        template = 'What is the correlation between restaurant id and street num of restaurants whose reviews are greater or equal than {INT}?'
        INT = self.generalinfo['review'].sample(1).iloc[0]
        ids = self.generalinfo[self.generalinfo['review'] >= INT]['id_restaurant']
        filted = self.location[self.location['id_restaurant'].isin(ids)]
        corr = filted['id_restaurant'].corr(filted['street_num'])
        question = template.format(INT=INT)

        rightIdx, choices = corrGen(corr)
        return question, corr, rightIdx, choices


if __name__ == '__main__':
    dbRoot = 'symDataset/scaledDB/8k/'
    dbn = 'restaurant'
    dbp = os.path.join(dbRoot, dbn, '0.sqlite')
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
    print(fi.q10())
    print(fi.q11())
    print(fi.q12())
    print(fi.q13())
