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

    def q5(self):
        template = 'How many students do {university_name} have in {year}?'
        row = self.university_year.sample(1)
        num_students = row['num_students'].iloc[0]
        university_id = row['university_id'].iloc[0]
        year = row['year'].iloc[0]
        university_name = self.university[self.university['id'] == university_id]['university_name'].iloc[0]
        question = template.format(university_name=university_name, year=year)
        return question, num_students

    def q6(self):
        template = 'Which university get most students in {year}?'
        year = self.university_year['year'].sample(1).iloc[0]
        filted = self.university_year[self.university_year['year'] == year]
        max_student = filted['num_students'].max()
        filted = filted[filted['num_students'] == max_student]
        university = self.university[self.university['id'].isin(filted['university_id'])]['university_name'].to_list()
        question = template.format(year=year)
        return question, university

    def q7(self):
        template = 'How many universities get over {num_students} students in {year}?'
        year = self.university_year['year'].sample(1).iloc[0]
        filted = self.university_year[self.university_year['year'] == year]
        num_students = filted['num_students'].sample(1).iloc[0] - 1
        filted = filted[filted['num_students'] > num_students]
        count = len(filted)
        question = template.format(num_students=num_students, year=year)
        return question, count

    def q8(self):
        template = 'What is the average student number in all universities in {year}?'
        year = self.university_year['year'].sample(1).iloc[0]
        filted = self.university_year[self.university_year['year'] == year]
        avg = filted['num_students'].mean()
        question = template.format(year=year)
        return question, avg

    def q9(self):
        template = 'What is the total student number in all universities in {year}?'
        year = self.university_year['year'].sample(1).iloc[0]
        filted = self.university_year[self.university_year['year'] == year]
        total = filted['num_students'].sum()
        question = template.format(year=year)
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
    print(fi.q5())
    print(fi.q6())
    print(fi.q7())
    print(fi.q8())
    print(fi.q9())
