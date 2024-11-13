import os
import random
from re import template
from unicodedata import numeric
import pandas as pd

import sys
sys.path.append('.')
from benchmarkUtils.database import DB
from symbolic.utils import choiceGen, stmtGen, numericalGen


class FoodFacilityInspections:
    retrieval = [
        ['Food_Facility_Restaurant_Inspection_Violations', 'Geocoded_Food_Facilities'],
        ['Geocoded_Food_Facilities'],
        ['Food_Facility_Restaurant_Inspection_Violations', 'Geocoded_Food_Facilities'],
        ['Food_Facility_Restaurant_Inspections', 'Geocoded_Food_Facilities'],
        ['Food_Facility_Restaurant_Inspections', 'Geocoded_Food_Facilities'],
        ['Food_Facility_Restaurant_Inspections', 'Geocoded_Food_Facilities'],
        ['Geocoded_Food_Facilities'],
        ['Food_Facility_Restaurant_Inspection_Violations', 'Geocoded_Food_Facilities'],
        ['Food_Facility_Restaurant_Inspection_Violations', 'Geocoded_Food_Facilities'],
        ['Food_Facility_Restaurant_Inspection_Violations', 'Geocoded_Food_Facilities']
    ]
    def __init__(self, dbp) -> None:
        db = DB(dbp)
        self.tables = db.tables

        self.facilities = self.tables['Geocoded_Food_Facilities']
        self.inspections = self.tables['Food_Facility_Restaurant_Inspections']
        self.violations = self.tables['Food_Facility_Restaurant_Inspection_Violations']
        # x longitude, y latitude

        self.facilities.rename(columns={'x': 'longitude', 'y': 'latitude'}, inplace=True)
        self.facilities['sq_feet'] = self.facilities['sq_feet'].fillna(0)
        self.facilities['sq_feet'] = self.facilities['sq_feet'].astype(int)
        self.facilities['longitude'] = abs(self.facilities['longitude'])
        self.facilities['latitude'] = abs(self.facilities['latitude'])
        self.facilities['seat_count'] = self.facilities['seat_count'].fillna(0)
        self.facilities['seat_count'] = self.facilities['seat_count'].astype(int)


    def q0(self):
        template = 'Which facility does violation id {violation_id} belong to?'
        row = self.violations.sample(1)
        violation_id = row['violation_id'].iloc[0]
        id = row['id'].iloc[0]
        facility = self.facilities[self.facilities['id'] == id]['facility_name'].iloc[0]
        question = template.format(violation_id=violation_id)

        rightIdx, choices = choiceGen(facility, self.facilities['facility_name'])
        stmts = stmtGen(choices,
                        'The violation_id {violation_id} belongs to <unk>.'.format(violation_id=violation_id))
        return question, facility, rightIdx, choices, stmts

    def q5(self):
        template = 'Which facility does inspection encounter {encounter} belong to?'
        row = self.inspections.sample(1)
        encounter = row['encounter'].iloc[0]
        id = row['id'].iloc[0]
        facility = self.facilities[self.facilities['id'] == id]['facility_name'].iloc[0]
        question = template.format(encounter=encounter)

        rightIdx, choices = choiceGen(facility, self.facilities['facility_name'])
        stmts = stmtGen(choices,
                        'The inspection encounter {encounter} belongs to <unk>.'.format(encounter=encounter))
        return question, facility, rightIdx, choices, stmts

    def q1(self):
        template = 'Which facility located in {city} has largest latitude (absolute value)?'
        city = self.facilities.sample(1)['city'].iloc[0]
        filted = self.facilities[self.facilities['city'] == city]
        max_val = filted['latitude'].max()
        facility = filted[filted['latitude'] == max_val]['facility_name'].to_list()
        question = template.format(city=city)

        rightIdx, choices = choiceGen(facility, self.facilities['facility_name'])
        stmts = stmtGen(choices,
                        'In {city}, <unk> has largest latitude (absolute value).'.format(city=city))
        return question, facility, rightIdx, choices, stmts

    def q6(self):
        template = 'Which facility located in {city} has largest longitude (absolute value)?'
        city = self.facilities.sample(1)['city'].iloc[0]
        filted = self.facilities[self.facilities['city'] == city]
        max_val = filted['longitude'].max()
        facility = filted[filted['longitude'] == max_val]['facility_name'].to_list()
        question = template.format(city=city)

        rightIdx, choices = choiceGen(facility, self.facilities['facility_name'])
        stmts = stmtGen(choices,
                        'In {city}, <unk> has largest longitude (absolute value).'.format(city=city))
        return question, facility, rightIdx, choices, stmts

    def q2(self):
        template = 'How many facilities are in violation low {low}?'
        low = self.violations.sample(1)['low'].iloc[0]
        filted = self.violations[self.violations['low'] == low]
        filted = self.facilities[self.facilities['id'].isin(filted['id'])]
        count = len(filted)
        question = template.format(low=low)

        rightIdx, choices = numericalGen(count)
        stmts = stmtGen(choices,
                        'There are <unk> facilities in violation low {low}.'.format(low=low))
        return question, count, rightIdx, choices, stmts

    def q7(self):
        template = 'How many facilities are in violation medium {medium}?'
        medium = self.violations.sample(1)['medium'].iloc[0]
        filted = self.violations[self.violations['medium'] == medium]
        filted = self.facilities[self.facilities['id'].isin(filted['id'])]
        count = len(filted)
        question = template.format(medium=medium)

        rightIdx, choices = numericalGen(count)
        stmts = stmtGen(choices,
                        'There are <unk> facilities in violation medium {medium}.'.format(medium=medium))
        return question, count, rightIdx, choices, stmts

    def q3(self):
        template = 'What is the average sq_feet of facilities that are inspected with {purpose} purpose?'
        purpose = self.inspections.sample(1)['purpose'].iloc[0]
        filted = self.inspections[self.inspections['purpose'] == purpose]
        filted = self.facilities[self.facilities['id'].isin(filted['id'])]
        avg = filted['sq_feet'].mean()
        question = template.format(purpose=purpose)

        rightIdx, choices = numericalGen(avg)
        stmts = stmtGen(choices,
                        'The average sq_feet of facilities that are inspected with {purpose} purpose is <unk>.'.format(purpose=purpose))
        return question, avg, rightIdx, choices, stmts

    def q4(self):
        template = 'What is the total sq_feet of facilities that are inspected with {purpose} purpose?'
        purpose = self.inspections.sample(1)['purpose'].iloc[0]
        filted = self.inspections[self.inspections['purpose'] == purpose]
        filted = self.facilities[self.facilities['id'].isin(filted['id'])]
        total = filted['sq_feet'].sum()
        question = template.format(purpose=purpose)

        rightIdx, choices = numericalGen(total)
        stmts = stmtGen(choices,
                        'The total sq_feet of facilities that are inspected with {purpose} purpose is <unk>.'.format(purpose=purpose))
        return question, total, rightIdx, choices, stmts

    def q8(self):
        template = 'What is the average sq_feet of facilities in violation high {high}?'
        high = self.violations.sample(1)['high'].iloc[0]
        filted = self.violations[self.violations['high'] == high]
        filted = self.facilities[self.facilities['id'].isin(filted['id'])]
        avg = filted['sq_feet'].mean()
        question = template.format(high=high)

        rightIdx, choices = numericalGen(avg)
        stmts = stmtGen(choices,
                        'The average sq_feet of facilities in violation high {high} is <unk>.'.format(high=high))
        return question, avg, rightIdx, choices, stmts

    def q9(self):
        template = 'What is the total sq_feet of facilities in violation high {high}?'
        high = self.violations.sample(1)['high'].iloc[0]
        filted = self.violations[self.violations['high'] == high]
        filted = self.facilities[self.facilities['id'].isin(filted['id'])]
        total = filted['sq_feet'].sum()
        question = template.format(high=high)

        rightIdx, choices = numericalGen(total)
        stmts = stmtGen(choices,
                        'The total sq_feet of facilities in violation high {high} is <unk>.'.format(high=high))
        return question, total, rightIdx, choices, stmts

    def q10(self):
        template = 'How many seats are {facility_name0} more than {facility_name1}?'
        rows = self.facilities[self.facilities['seat_count'] > 0].sample(2)
        facility_name0 = rows['facility_name'].iloc[0]
        facility_name1 = rows['facility_name'].iloc[1]
        diff = rows['seat_count'].iloc[0] - rows['seat_count'].iloc[1]
        question = template.format(facility_name0=facility_name0, facility_name1=facility_name1)

        rightIdx, choices = numericalGen(diff)
        return question, diff, rightIdx, choices

    def q11(self):
        template = 'How many sq_feet are {facility_name0} more than {facility_name1}?'
        rows = self.facilities[self.facilities['sq_feet'] > 0].sample(2)
        facility_name0 = rows['facility_name'].iloc[0]
        facility_name1 = rows['facility_name'].iloc[1]
        diff = rows['sq_feet'].iloc[0] - rows['sq_feet'].iloc[1]
        question = template.format(facility_name0=facility_name0, facility_name1=facility_name1)

        rightIdx, choices = numericalGen(diff)
        return question, diff, rightIdx, choices


if __name__ == '__main__':
    dbRoot = 'symDataset/scaledDB/8k/'
    dbn = 'food_facility_inspections'
    dbp = os.path.join(dbRoot, dbn, '0.sqlite')
    fi = FoodFacilityInspections(dbp)
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
