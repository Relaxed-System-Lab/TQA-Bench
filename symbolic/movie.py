import os
import pandas as pd

import sys
sys.path.append('.')
from benchmarkUtils.database import DB
from symbolic.utils import choiceGen, stmtGen, numericalGen


class Movie:
    def __init__(self, dbp) -> None:
        db = DB(dbp)
        self.tables = db.tables

        self.actor = self.tables['actor']
        self.movie = self.tables['movie']
        self.characters = self.tables['characters']

        self.retrieval = [
            ['characters', 'movie', 'actor'],
            ['movie'],
            ['movie'],
            ['actor'],
            ['movie'],
            ['movie'],
            ['movie'],
            ['movie'],
            ['movie'],
            ['movie']
        ]

    def q0(self):
        template = 'What is the name of character played by {Name} in {Title}?'
        merged_df = pd.merge(self.characters, self.movie, left_on='MovieID', right_on='MovieID')
        merged_df = pd.merge(merged_df, self.actor, left_on='ActorID', right_on='ActorID')
        sample_row = merged_df.sample(1)
        character_name = sample_row['Character Name'].iloc[0]
        name = sample_row['Name'].iloc[0]
        title = sample_row['Title'].iloc[0]
        question = template.format(Name=name, Title=title)

        rightIdx, choices = choiceGen(character_name, self.characters['Character Name'])
        stmts = stmtGen(choices,
                        'The name of character played by {Name} in {Title} is <unk>.'.format(Name=name, Title=title))
        return question, character_name, rightIdx, choices, stmts

    def q1(self):
        template = 'Which {Genre} movie get the highest rating?'
        genre = self.movie['Genre'].sample(1).iloc[0]
        filted = self.movie[self.movie['Genre'] == genre]
        max_score = filted['Rating'].max()
        max_filted = filted[filted['Rating'] == max_score]
        valid_movie = max_filted['Title'].to_list()
        question = template.format(Genre=genre)

        rightIdx, choices = choiceGen(valid_movie, self.movie['Title'])
        stmts = stmtGen(choices,
                        '<unk> get the highest rating in {Genre} movies.'.format(Genre=genre))
        return question, valid_movie, rightIdx, choices, stmts

    def q2(self):
        template = 'How many {Genre} movie get over {REAL:.1f} rating?'
        genre = self.movie['Genre'].sample(1).iloc[0]
        REAL = self.movie['Rating'].sample(1).iloc[0] - 0.1
        filted = self.movie[self.movie['Genre'] == genre]
        filted = filted[filted['Rating'] > REAL]
        count = len(filted)
        question =  template.format(Genre=genre, REAL=REAL)

        rightIdx, choices = numericalGen(count)
        stmts = stmtGen(choices,
                        'There are <unk> {Genre} movies get over {REAL:.1f} rating.'.format(Genre=genre, REAL=REAL))
        return question, count, rightIdx, choices, stmts

    def q3(self):
        template = 'What is the average height of {Birth_Country} actors?'
        birth_country = self.actor['Birth Country'].sample(1).iloc[0]
        filted = self.actor[self.actor['Birth Country'] == birth_country]
        avg_hight = filted['Height (Inches)'].mean()
        question = template.format(Birth_Country=birth_country)

        rightIdx, choices = numericalGen(avg_hight)
        stmts = stmtGen(choices,
                        'The average height of {Birth_Country} actors is <unk>.'.format(Birth_Country=birth_country))
        return question, avg_hight, rightIdx, choices, stmts

    def q4(self):
        template = 'What is the total runtime of the {Genre} movie?'
        genre = self.movie['Genre'].sample(1).iloc[0]
        filted = self.movie[self.movie['Genre'] == genre]
        total = filted['Runtime'].sum()
        question = template.format(Genre=genre)

        rightIdx, choices = numericalGen(total)
        stmts = stmtGen(choices,
                        'The total runtime of the {Genre} movie is <unk>.'.format(Genre=genre))
        return question, total, rightIdx, choices, stmts

    def q5(self):
        template = 'When did the {Title} released?'
        row = self.movie.sample(1)
        Title = row['Title'].iloc[0]
        release_date = row['Release Date'].iloc[0]
        question = template.format(Title=Title)

        rightIdx, choices = choiceGen(release_date, self.movie['Release Date'])
        stmts = stmtGen(choices,
                        'The {Title} released in <unk>.'.format(Title=Title))
        return question, release_date, rightIdx, choices, stmts

    def q6(self):
        template = 'Which {Genre} movie get the highest budget?'
        genre = self.movie['Genre'].sample(1).iloc[0]
        filted = self.movie[self.movie['Genre'] == genre]
        max_budget = filted['Budget'].max()
        max_filted = filted[filted['Budget'] == max_budget]
        valid_movie = max_filted['Title'].to_list()
        question = template.format(Genre=genre)

        rightIdx, choices = choiceGen(valid_movie, self.movie['Title'])
        stmts = stmtGen(choices,
                        'The <unk> get the highest budget in {Genre} movies.'.format(Genre=genre))
        return question, valid_movie, rightIdx, choices, stmts

    def q7(self):
        template = 'How many {Genre} movies get greater or equal to {INT} budget?'
        genre = self.movie['Genre'].sample(1).iloc[0]
        filted = self.movie[self.movie['Genre'] == genre]
        INT = filted['Budget'].sample(1).iloc[0]
        filted = filted[filted['Budget'] >= INT]
        count = len(filted)
        question = template.format(Genre=genre, INT=INT)

        rightIdx, choices = numericalGen(count)
        stmts = stmtGen(choices,
                        'There are <unk> {Genre} movies get greater or equal to {INT} budget.'.format(Genre=genre, INT=INT))
        return question, count, rightIdx, choices, stmts

    def q8(self):
        template = 'What is the average budget of {Genre} movies with greater or equal to {REAL} rating?'
        genre = self.movie['Genre'].sample(1).iloc[0]
        filted = self.movie[self.movie['Genre'] == genre]
        REAL = filted['Rating'].sample(1).iloc[0]
        filted = filted[filted['Rating'] >= REAL]
        avg = filted['Budget'].mean()
        question = template.format(Genre=genre, REAL=REAL)

        rightIdx, choices = numericalGen(avg)
        stmts = stmtGen(choices,
                        'The average budget of {Genre} movies with greater or equal to {REAL} rating is <unk>.'.format(Genre=genre, REAL=REAL))
        return question, avg, rightIdx, choices, stmts

    def q9(self):
        template = 'What is the total budget of moives that is greater or equal to {REAL} rating?'
        REAL = self.movie['Rating'].sample(1).iloc[0]
        filted = self.movie[self.movie['Rating'] >= REAL]
        total = filted['Budget'].sum()
        question = template.format(REAL=REAL)

        rightIdx, choices = numericalGen(total)
        stmts = stmtGen(choices,
                        'The total budget of moives that is greater or equal to {REAL} rating is <unk>.'.format(REAL=REAL))
        return question, total, rightIdx, choices, stmts


if __name__ == '__main__':
    dbRoot = 'dataset/optmizedScaledDB/8k/'
    dbn = 'movie'
    dbp = os.path.join(dbRoot, dbn, f'{dbn}.sqlite')
    fi = Movie(dbp)
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
