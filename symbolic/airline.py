import os
from random import choice, choices
import pandas as pd

import sys
sys.path.append('.')
from benchmarkUtils.database import DB
from symbolic.utils import choiceGen, stmtGen, numericalGen, corrGen


class Airline:
    retrieval = [
        ['Airports'],
        ['Airlines', 'Airports'],
        ['Airlines', 'Airports'],
        ['Airlines', 'Airports'],
        ['Airlines', 'Airports'],
        ['Air_Carriers'],
        ['Airlines', 'Airports'],
        ['Airlines', 'Airports'],
        ['Airlines', 'Airports'],
        ['Airlines', 'Airports']
    ]
    def __init__(self, dbp) -> None:
        db = DB(dbp)
        self.tables = db.tables

        self.Air_Carriers = self.tables['Air_Carriers']
        self.Airports = self.tables['Airports']
        self.Airlines = self.tables['Airlines']

    def q0(self):
        template = 'What is the description of airport {Code}?'
        row = self.Airports.sample(1)
        Code = row['Code'].iloc[0]
        Description = row['Description'].iloc[0]
        question = template.format(Code=Code)

        rightIdx, choices = choiceGen(Description, self.Airports['Description'])
        stmts = stmtGen(choices,
                        'The description of airport {Code} is <unk>.'.format(Code=Code))
        return question, Description, rightIdx, choices, stmts

    def q1(self):
        template = 'Which airport lands most flights start from {ORIGIN}?'
        ORIGIN = self.Airlines['ORIGIN'].sample(1).iloc[0]
        origin_description = self.Airports[self.Airports['Code'] == ORIGIN]['Description'].iloc[0]
        filted = self.Airlines[self.Airlines['ORIGIN'] == ORIGIN]
        max_count = filted['DEST'].value_counts()
        max_val = max_count.max()
        lands_airport = max_count[max_count == max_val].index
        dest_description = self.Airports[self.Airports['Code'].isin(lands_airport)]['Description'].to_list()
        question = template.format(ORIGIN=origin_description)

        rightIdx, choices = choiceGen(dest_description, self.Airports['Description'])
        stmts = stmtGen(choices,
                        'The airport <unk> lands most flights start from {ORIGIN}.'.format(ORIGIN=origin_description))
        return question, dest_description, rightIdx, choices, stmts

    def q2(self):
        template = 'How many airlines land in {DEST}?'
        DEST = self.Airlines['DEST'].sample(1).iloc[0]
        dest_description = self.Airports[self.Airports['Code'] == DEST]['Description'].iloc[0]
        filted = self.Airlines[self.Airlines['DEST'] == DEST]
        land_airline = len(filted)
        question = template.format(DEST=dest_description)

        rightIdx, choices = numericalGen(land_airline)
        stmts = stmtGen(choices,
                        'There are <unk> airlines land in {DEST}.'.format(DEST=dest_description))
        return question, land_airline, rightIdx, choices, stmts

    def q3(self):
        template = 'What is the average flight delay (ARR_DELAY) that land in {DEST}?'
        DEST = self.Airlines['DEST'].sample(1).iloc[0]
        dest_description = self.Airports[self.Airports['Code'] == DEST]['Description'].iloc[0]
        filted = self.Airlines[self.Airlines['DEST'] == DEST]
        avg = filted['ARR_DELAY'].mean()
        question = template.format(DEST=dest_description)

        rightIdx, choices = numericalGen(avg)
        stmts = stmtGen(choices,
                        'The average flight delay (ARR_DELAY) that land in {DEST} is <unk>.'.format(DEST=dest_description))
        return question, avg, rightIdx, choices, stmts

    def q4(self):
        template = 'What is the total flight delay (DEP_DELAY) that start from {ORIGIN}?'
        ORIGIN = self.Airlines['ORIGIN'].sample(1).iloc[0]
        origin_description = self.Airports[self.Airports['Code'] == ORIGIN]['Description'].iloc[0]
        filted = self.Airlines[self.Airlines['ORIGIN'] == ORIGIN]
        total = filted['DEP_DELAY'].sum()
        question = template.format(ORIGIN=origin_description)

        rightIdx, choices = numericalGen(total)
        stmts = stmtGen(choices,
                        'The total flight delay (DEP_DELAY) that start from {ORIGIN} is <unk>.'.format(ORIGIN=origin_description))
        return question, total, rightIdx, choices, stmts

    def q5(self):
        template = 'What is the description of air carrier {Code}?'
        row = self.Air_Carriers.sample(1)
        Code = row['Code'].iloc[0]
        Description = row['Description'].iloc[0]
        question = template.format(Code=Code)

        rightIdx, choices = choiceGen(Description, self.Air_Carriers['Description'])
        stmts = stmtGen(choices,
                        'The description of air carrier {Code} is <unk>.'.format(Code=Code))
        return question, Description, rightIdx, choices, stmts

    def q6(self):
        template = 'Which airport starts most flights land on {DEST}?'
        DEST = self.Airlines['DEST'].sample(1).iloc[0]
        dest_description = self.Airports[self.Airports['Code'] == DEST]['Description'].iloc[0]
        filted = self.Airlines[self.Airlines['DEST'] == DEST]
        max_count = filted['ORIGIN'].value_counts()
        max_val = max_count.max()
        lands_airport = max_count[max_count == max_val].index
        origin_description = self.Airports[self.Airports['Code'].isin(lands_airport)]['Description'].to_list()
        question = template.format(DEST=dest_description)

        rightIdx, choices = choiceGen(origin_description, self.Airports['Description'])
        stmts = stmtGen(choices,
                        'The airport <unk> starts most flights land on {DEST}.'.format(DEST=dest_description))
        return question, origin_description, rightIdx, choices, stmts

    def q7(self):
        template = 'How many airlines start from {ORIGIN}?'
        ORIGIN = self.Airlines['ORIGIN'].sample(1).iloc[0]
        origin_description = self.Airports[self.Airports['Code'] == ORIGIN]['Description'].iloc[0]
        filted = self.Airlines[self.Airlines['ORIGIN'] == ORIGIN]
        land_airline = len(filted)
        question = template.format(ORIGIN=origin_description)

        rightIdx, choices = numericalGen(land_airline)
        stmts = stmtGen(choices,
                        'There are <unk> airlines start from {ORIGIN}.'.format(ORIGIN=origin_description))
        return question, land_airline, rightIdx, choices, stmts

    def q8(self):
        template = 'What is the average flight delay (DEP_DELAY) that start from {ORIGIN}?'
        ORIGIN = self.Airlines['ORIGIN'].sample(1).iloc[0]
        origin_description = self.Airports[self.Airports['Code'] == ORIGIN]['Description'].iloc[0]
        filted = self.Airlines[self.Airlines['ORIGIN'] == ORIGIN]
        avg = filted['DEP_DELAY'].mean()
        question = template.format(ORIGIN=origin_description)

        rightIdx, choices = numericalGen(avg)
        stmts = stmtGen(choices,
                        'The average flight delay (DEP_DELAY) that start from {ORIGIN} is <unk>.'.format(ORIGIN=origin_description))
        return question, avg, rightIdx, choices, stmts

    def q9(self):
        template = 'What is the total flight delay (ARR_DELAY) that land in {DEST}?'
        DEST = self.Airlines['DEST'].sample(1).iloc[0]
        dest_description = self.Airports[self.Airports['Code'] == DEST]['Description'].iloc[0]
        filted = self.Airlines[self.Airlines['DEST'] == DEST]
        total = filted['ARR_DELAY'].sum()
        question = template.format(DEST=dest_description)

        rightIdx, choices = numericalGen(total)
        stmts = stmtGen(choices,
                        'The total flight delay (ARR_DELAY) that land in {DEST} is <unk>.'.format(DEST=dest_description))
        return question, total, rightIdx, choices, stmts

    def q10(self):
        template = 'What is the average total delay (ARR_DELAY-DEP_DELAY) of {description}?'
        id = self.Airlines.sample(1)['OP_CARRIER_AIRLINE_ID'].iloc[0]
        description = self.Air_Carriers[self.Air_Carriers['Code'] == id]['Description'].iloc[0]
        filted = self.Airlines[self.Airlines['OP_CARRIER_AIRLINE_ID'] == id]
        avg = (filted['ARR_DELAY'] - filted['DEP_DELAY']).mean()
        question = template.format(description=description)

        rightIdx, choices = numericalGen(avg)
        return question, avg, rightIdx, choices

    def q11(self):
        template = 'What is the average total fly time (ARR_TIME-DEP_TIME) of {description}?'
        id = self.Airlines.sample(1)['OP_CARRIER_AIRLINE_ID'].iloc[0]
        description = self.Air_Carriers[self.Air_Carriers['Code'] == id]['Description'].iloc[0]
        filted = self.Airlines[self.Airlines['OP_CARRIER_AIRLINE_ID'] == id]
        avg = (filted['ARR_TIME'] - filted['DEP_TIME']).mean()
        question = template.format(description=description)

        rightIdx, choices = numericalGen(avg)
        return question, avg, rightIdx, choices

    def q12(self):
        template = 'What is the correlation between department delay and arrive delay of air carrier {description}?'
        aid = self.Airlines[self.Airlines['OP_CARRIER_AIRLINE_ID'].duplicated()].sample(1)['OP_CARRIER_AIRLINE_ID'].iloc[0]
        # aid = self.Airlines.sample(1)['OP_CARRIER_AIRLINE_ID'].iloc[0]
        description = self.Air_Carriers[self.Air_Carriers['Code'] == aid]['Description'].iloc[0]
        filted = self.Airlines[self.Airlines['OP_CARRIER_AIRLINE_ID'] == aid]
        corr = filted['ARR_DELAY'].corr(filted['DEP_DELAY'])
        question = template.format(description=description)

        rightIdx, choices = corrGen(corr)
        return question, corr, rightIdx, choices

    def q13(self):
        template = 'What is the correlation between department delay and arrive delay of airlines whose depart delay are greater or equal than {INT}?'
        dep_delay = self.Airlines[self.Airlines['DEP_DELAY'].notna()].sample(1)['DEP_DELAY'].iloc[0]
        filted = self.Airlines[self.Airlines['DEP_DELAY'] >= dep_delay]
        corr = filted['ARR_DELAY'].corr(filted['DEP_DELAY'])
        question = template.format(INT=dep_delay)

        rightIdx, choices = corrGen(corr)
        return question, corr, rightIdx, choices


if __name__ == '__main__':
    dbRoot = 'symDataset/scaledDB/8k/'
    dbn = 'airline'
    dbp = os.path.join(dbRoot, dbn, f'0.sqlite')
    fi = Airline(dbp)
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
