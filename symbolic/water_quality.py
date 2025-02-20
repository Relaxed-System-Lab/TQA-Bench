import os
import random
import pandas as pd

import sys
sys.path.append('.')
from benchmarkUtils.database import DB
from symbolic.utils import choiceGen, corrGen, stmtGen, numericalGen


class WaterQuality:
    retrieval = [
        ['stations'],
        ['stations'],
        ['stations', 'field_results'],
        ['stations'],
        ['stations'],
        ['stations'],
        ['stations'],
        ['stations', 'lab_results'],
        ['stations'],
        ['stations']
    ]
    def __init__(self, dbp) -> None:
        db = DB(dbp)
        self.tables = db.tables

        self.stations = self.tables['stations']
        self.period_of_record = self.tables['period_of_record']
        self.field_results = self.tables['field_results']
        self.lab_results = self.tables['lab_results']

        self.stations['latitude'] = abs(self.stations['latitude'])
        self.stations['longitude'] = abs(self.stations['longitude'])


    def q0(self):
        template = 'Where is the {full_station_name}?'
        row = self.stations.sample(1)
        full_station_name = row['full_station_name'].iloc[0]
        county = row['county_name'].iloc[0]
        question = template.format(full_station_name=full_station_name)

        rightIdx, choices = choiceGen(county, self.stations['county_name'])
        stmts = stmtGen(choices,
                        'the {full_station_name} is located in <unk>.'.format(full_station_name=full_station_name))
        return question, county, rightIdx, choices, stmts

    def q5(self):
        template = 'How many samples do {full_station_name} has?'
        row = self.stations.sample(1)
        full_station_name = row['full_station_name'].iloc[0]
        sample_count = row['sample_count'].iloc[0]
        question = template.format(full_station_name=full_station_name)

        rightIdx, choices = choiceGen(sample_count, self.stations['sample_count'])
        stmts = stmtGen(choices,
                        '{full_station_name} has <unk> samples.'.format(full_station_name=full_station_name))
        return question, sample_count, rightIdx, choices, stmts

    def q1(self):
        template = 'Which station that located greater or equal than {latitude} latitude (absolute value) has most samples?'
        latitude = self.stations['latitude'].sample(1).iloc[0]
        filted = self.stations[self.stations['latitude'] >= latitude]
        max_val = filted['sample_count'].max()
        full_station_name = filted[filted['sample_count'] == max_val]['full_station_name'].to_list()
        question = template.format(latitude=latitude)

        rightIdx, choices = choiceGen(full_station_name, self.stations['full_station_name'])
        stmts = stmtGen(choices,
                        'Station <unk> that located greater or equal than {latitude} latitude (absolute value) has most samples.'.format(latitude=latitude))
        return question, full_station_name, rightIdx, choices, stmts

    def q6(self):
        template = 'Which station that located greater or equal than {longitude} longitude (absolute value) has most samples?'
        longitude = self.stations['longitude'].sample(1).iloc[0]
        filted = self.stations[self.stations['longitude'] >= longitude]
        max_val = filted['sample_count'].max()
        full_station_name = filted[filted['sample_count'] == max_val]['full_station_name'].to_list()
        question = template.format(longitude=longitude)

        rightIdx, choices = choiceGen(full_station_name, self.stations['full_station_name'])
        stmts = stmtGen(choices,
                        'Station <unk> that located greater or equal than {longitude} longitude (absolute value) has most samples.'.format(longitude=longitude))
        return question, full_station_name, rightIdx, choices, stmts

    def q2(self):
        template = 'How many field results are from {county_name} stations?'
        county = self.stations.sample(1)['county_name'].iloc[0]
        filted = self.stations[self.stations['county_name'] == county]
        filted = filted[filted['station_id'].isin(self.field_results['station_id'])]
        count = len(filted)
        question = template.format(county_name=county)

        rightIdx, choices = numericalGen(count)
        stmts = stmtGen(choices,
                        'There are <unk> field results are from {county_name} stations.'.format(county_name=county))
        return question, count, rightIdx, choices, stmts

    def q7(self):
        template = 'How many lab results are from {county_name} stations?'
        county = self.stations.sample(1)['county_name'].iloc[0]
        filted = self.stations[self.stations['county_name'] == county]
        filted = filted[filted['station_id'].isin(self.lab_results['station_id'])]
        count = len(filted)
        question = template.format(county_name=county)

        rightIdx, choices = numericalGen(count)
        stmts = stmtGen(choices,
                        'There are <unk> lab results are from {county_name} stations.'.format(county_name=county))
        return question, count, rightIdx, choices, stmts

    def q3(self):
        template = 'What is the average sample count of stations that located greater or equal than {latitude} latitude (absolute value)?'
        latitude = self.stations.sample(1)['latitude'].iloc[0]
        filted = self.stations[self.stations['latitude'] >= latitude]
        avg = filted['sample_count'].mean()
        question = template.format(latitude=latitude)

        rightIdx, choices = numericalGen(avg)
        stmts = stmtGen(choices,
                        'The average sample count of stations that located greater or equal than {latitude} latitude (absolute value) is <unk>.'.format(latitude=latitude))
        return question, avg, rightIdx, choices, stmts

    def q8(self):
        template = 'What is the average sample count of stations that located greater or equal than {longitude} longitude (absolute value)?'
        longitude = self.stations.sample(1)['longitude'].iloc[0]
        filted = self.stations[self.stations['longitude'] >= longitude]
        avg = filted['sample_count'].mean()
        question = template.format(longitude=longitude)

        rightIdx, choices = numericalGen(avg)
        stmts = stmtGen(choices,
                        'The average sample count of stations that located greater or equal than {longitude} longitude (absolute value) is <unk>.'.format(longitude=longitude))
        return question, avg, rightIdx, choices, stmts

    def q4(self):
        template = 'What is the total sample count of stations that located greater or equal than {latitude} latitude (absolute value)?'
        latitude = self.stations.sample(1)['latitude'].iloc[0]
        filted = self.stations[self.stations['latitude'] >= latitude]
        total = filted['sample_count'].sum()
        question = template.format(latitude=latitude)

        rightIdx, choices = numericalGen(total)
        stmts = stmtGen(choices,
                        'The total sample count of stations that located greater or equal than {latitude} latitude (absolute value) is <unk>.'.format(latitude=latitude))
        return question, total, rightIdx, choices, stmts

    def q9(self):
        template = 'What is the total sample count of stations that located greater or equal than {longitude} longitude (absolute value)?'
        longitude = self.stations.sample(1)['longitude'].iloc[0]
        filted = self.stations[self.stations['longitude'] >= longitude]
        total = filted['sample_count'].sum()
        question = template.format(longitude=longitude)

        rightIdx, choices = numericalGen(total)
        stmts = stmtGen(choices,
                        'The average sample count of stations that located greater or equal than {longitude} longitude (absolute value) is <unk>.'.format(longitude=longitude))
        return question, total, rightIdx, choices, stmts

    def q10(self):
        template = 'How many samples are {full_station_name0} more than {full_station_name1}?'
        rows = self.stations.sample(2)
        full_station_name0 = rows['full_station_name'].iloc[0]
        full_station_name1 = rows['full_station_name'].iloc[1]
        diff = rows['sample_count'].iloc[0] - rows['sample_count'].iloc[1]
        question = template.format(full_station_name0=full_station_name0, full_station_name1=full_station_name1)

        rightIdx, choices = numericalGen(diff)
        return question, diff, rightIdx, choices

    def q11(self):
        template = 'How many average samples are {station_type0} stations more than {station_type1} stations?'
        station_types = self.stations['station_type'].drop_duplicates().sample(2)
        station_type0 = station_types.iloc[0]
        station_type1 = station_types.iloc[1]
        diff = self.stations[self.stations['station_type'] == station_type1]['sample_count'].mean() - self.stations[self.stations['station_type'] == station_type1]['sample_count'].mean()
        question = template.format(station_type0=station_type0, station_type1=station_type1)

        rightIdx, choices = numericalGen(diff)
        return question, diff, rightIdx, choices

    def q12(self):
        template = 'What is the correlation between station id and sample count of stations whose type is {station_type}?'
        station_type = self.stations['station_type'].sample(1).iloc[0]
        filted = self.stations[self.stations['station_type'] == station_type]
        corr = filted['station_id'].corr(filted['sample_count'])
        question = template.format(station_type=station_type)

        rightIdx, choices = corrGen(corr)
        return question, corr, rightIdx, choices

    def q13(self):
        template = 'What is the correlation between station id and sample count of stations whose sample count are greater or equal than {INT}?'
        INT = self.stations['sample_count'].sample(1).iloc[0]
        filted = self.stations[self.stations['sample_count'] >= INT]
        corr = filted['station_id'].corr(filted['sample_count'])
        question = template.format(INT=INT)

        rightIdx, choices = corrGen(corr)
        return question, corr, rightIdx, choices


if __name__ == '__main__':
    dbRoot = 'symDataset/scaledDB/8k/'
    dbn = 'water_quality'
    dbp = os.path.join(dbRoot, dbn, '0.sqlite')
    fi = WaterQuality(dbp)
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
