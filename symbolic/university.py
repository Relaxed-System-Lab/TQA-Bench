import os
from re import template
import pandas as pd

import sys
sys.path.append('.')
from benchmarkUtils.database import DB


class University:
    def __init__(self, dbp) -> None:
        db = DB(dbp)
        self.tables = db.tables

        self.country = self.tables['country']
        self.ranking_system = self.tables['ranking_system']
        self.ranking_criteria = self.tables['ranking_criteria']
        self.university = self.tables['university']
        self.university_ranking_year = self.tables['university_ranking_year']
        self.university_year = self.tables['university_year']

    def q0(self):
        template = 'How many scores do {university_name} get in {year}?'
        row = self.university_ranking_year.sample(1)
        score = row['score'].iloc[0]
        university_id = row['university_id'].iloc[0]
        year = row['year'].iloc[0]
        university_name = self.university[self.university['id'] == university_id]['university_name'].iloc[0]
        question = template.format(university_name=university_name, year=year)
        return question, score

    def q1(self):
        template = 'Which university get the most score in {year}?'
        year = self.university_ranking_year['year'].sample(1).iloc[0]
        filted = self.university_ranking_year[self.university_ranking_year['year'] == year]
        max_score = filted['score'].max()
        filted = filted[filted['score'] == max_score]
        university = self.university[self.university['id'].isin(filted['university_id'])]['university_name'].to_list()
        question = template.format(year=year)
        return question, university

    def q2(self):
        template = 'How many universities get over {score} score in {year}?'
        year = self.university_ranking_year['year'].sample(1).iloc[0]
        filted = self.university_ranking_year[self.university_ranking_year['year'] == year]
        score = filted['score'].sample(1).iloc[0] - 1
        filted = filted[filted['score'] > score]
        count = len(filted)
        question = template.format(score=score, year=year)
        return question, count

    def q3(self):
        template = 'What is the average score of {university_name} in these years?'
        university_id = self.university_ranking_year['university_id'].sample(1).iloc[0]
        university_name = self.university[self.university['id'] == university_id]['university_name'].iloc[0]
        filted = self.university_ranking_year[self.university_ranking_year['university_id'] == university_id]
        avg = filted['score'].mean()
        question = template.format(university_name=university_name)
        return question, avg

    def q4(self):
        template = 'What is the total score of {university_name} in these years?'
        university_id = self.university_ranking_year['university_id'].sample(1).iloc[0]
        university_name = self.university[self.university['id'] == university_id]['university_name'].iloc[0]
        filted = self.university_ranking_year[self.university_ranking_year['university_id'] == university_id]
        total = filted['score'].sum()
        question = template.format(university_name=university_name)
        return question, total


if __name__ == '__main__':
    dbRoot = 'dataset/optmizedScaledDB/8k/'
    dbn = 'university'
    dbp = os.path.join(dbRoot, dbn, f'{dbn}.sqlite')
    fi = University(dbp)
    print(fi.q0())
    print(fi.q1())
    print(fi.q2())
    print(fi.q3())
    print(fi.q4())
