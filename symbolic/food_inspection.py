import os
from re import template
import pandas as pd

import sys

sys.path.append('.')
from benchmarkUtils.database import DB

class FoodInspection:
    def __init__(self, dbp) -> None:
        db = DB(dbp)
        self.tables = db.tables

        self.businesses = self.tables['businesses']
        # 有时候会有CA, Ca的区别
        self.businesses['owner_state'] = self.businesses['owner_state'].str.upper()
        self.inspections = self.tables['inspections']
        self.violations = self.tables['violations']

    def q0(self):
        template = 'What is the address of business_id {business_id}?'
        business_id = self.businesses['business_id'].sample(1).iloc[0]
        address = self.businesses[self.businesses['business_id'] == business_id]['address'].iloc[0]
        question = template.format(business_id=business_id)
        return question, address

    def q1(self):
        template = 'Which state has most {risk_category} violations?'
        risk_category = self.violations['risk_category'].sample(1).iloc[0]
        risk_violations = self.violations[self.violations['risk_category'] == risk_category]
        merged_df = pd.merge(risk_violations, self.businesses, left_on='business_id', right_on='business_id')
        max_count = merged_df['owner_state'].value_counts()
        most_state = max_count[max_count == max_count.max()].index.to_list()
        question = template.format(risk_category=risk_category)
        return question, most_state

    def q2(self):
        template = 'How many violations are happenend in the state {owner_state}?'
        merged_df = pd.merge(self.violations, self.businesses, left_on='business_id', right_on='business_id')
        owner_state = merged_df['owner_state'].sample(1).iloc[0]
        happen_owner_state = merged_df[merged_df['owner_state'] == owner_state]
        count = len(happen_owner_state)
        question = template.format(owner_state=owner_state)
        return question, count

    def q3(self):
        template = 'What is the average score of {type} inspections?'
        type = self.inspections['type'].sample(1).iloc[0]
        filted = self.inspections[self.inspections['type'] == type]
        avg = filted['score'].mean()
        question = template.format(type=type)
        return question, avg

    def q4(self):
        template = 'What is the total score of inspections happened in {owner_state}?'
        merged_df = pd.merge(self.businesses, self.inspections, left_on='business_id', right_on='business_id')
        owner_state = merged_df['owner_state'].sample(1).iloc[0]
        filted = merged_df[merged_df['owner_state'] == owner_state]
        total = filted['score'].sum()
        question = template.format(owner_state=owner_state)
        return question, total

    def q5(self):
        template = 'What is the risk category of business_id {business_id}?'
        business_id = self.violations['business_id'].sample(1).iloc[0]
        risk_category = self.violations[self.violations['business_id'] == business_id]['risk_category'].iloc[0]
        question = template.format(business_id=business_id)
        return question, risk_category

    def q6(self):
        template = 'Which business in {owner_state} gets highest score in the inspection?'
        merged_df = pd.merge(self.inspections, self.businesses, left_on='business_id', right_on='business_id')
        owner_state = merged_df['owner_state'].sample(1).iloc[0]
        filted = merged_df[merged_df['owner_state'] == owner_state]
        max_val = filted['score'].max()
        filted = merged_df[merged_df['score'] == max_val]['name'].to_list()
        question = template.format(owner_state=owner_state)
        return question, filted

    def q7(self):
        template = 'How many businesses get more than {INT} scores?'
        sp = self.inspections['score'].sample(1).iloc[0]
        INT = (1 if pd.isna(sp) else sp) - 1
        filted = self.inspections[self.inspections['score'] > INT]
        count = len(filted)
        question = template.format(INT=INT)
        return question, count

    def q8(self):
        template = 'What is the average score of {owner_state} in inspections?'
        merged_df = pd.merge(self.inspections, self.businesses, left_on='business_id', right_on='business_id')
        owner_state = merged_df['owner_state'].sample(1).iloc[0]
        filted = merged_df[merged_df['owner_state'] == owner_state]
        avg = filted['score'].mean()
        question = template.format(owner_state=owner_state)
        return question, avg

    def q9(self):
        template = 'What is the total score of {owner_state} in inspections?'
        merged_df = pd.merge(self.inspections, self.businesses, left_on='business_id', right_on='business_id')
        owner_state = merged_df['owner_state'].sample(1).iloc[0]
        filted = merged_df[merged_df['owner_state'] == owner_state]
        total = filted['score'].sum()
        question = template.format(owner_state=owner_state)
        return question, total

if __name__ == '__main__':
    dbRoot = 'dataset/optmizedScaledDB/8k/'
    dbn = 'food_inspection'
    dbp = os.path.join(dbRoot, dbn, f'{dbn}.sqlite')
    fi = FoodInspection(dbp)
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
