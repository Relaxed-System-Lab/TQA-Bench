import os
import pandas as pd

import sys
sys.path.append('.')
from benchmarkUtils.database import DB


class Movie:
    def __init__(self, dbp) -> None:
        db = DB(dbp)
        self.tables = db.tables

        self.actor = self.tables['actor']
        self.movie = self.tables['movie']
        self.characters = self.tables['characters']

    def q0(self):
        template = 'What is the name of character played by {Name} in {Title}?'
        merged_df = pd.merge(self.characters, self.movie, left_on='MovieID', right_on='MovieID')
        merged_df = pd.merge(merged_df, self.actor, left_on='ActorID', right_on='ActorID')
        sample_row = merged_df.sample(1)
        character_name = sample_row['Character Name'].iloc[0]
        name = sample_row['Name'].iloc[0]
        title = sample_row['Title'].iloc[0]
        question = template.format(Name=name, Title=title)
        return question, character_name

    def q1(self):
        template = 'Which {Genre} movie get the highest rating?'
        genre = self.movie['Genre'].sample(1).iloc[0]
        filted = self.movie[self.movie['Genre'] == genre]
        max_score = filted['Rating'].max()
        max_filted = filted[filted['Rating'] == max_score]
        valid_movie = max_filted['Title'].to_list()
        question = template.format(Genre=genre)
        return question, valid_movie

    def q2(self):
        template = 'How many {Genre} movie get over {REAL:.1f} rating?'
        genre = self.movie['Genre'].sample(1).iloc[0]
        REAL = self.movie['Rating'].sample(1).iloc[0] - 0.1
        filted = self.movie[self.movie['Genre'] == genre]
        filted = filted[filted['Rating'] > REAL]
        count = len(filted)
        question =  template.format(Genre=genre, REAL=REAL)
        return question, count

    def q3(self):
        template = 'What is the average height of {Birth_Country} actors?'
        birth_country = self.actor['Birth Country'].sample(1).iloc[0]
        filted = self.actor[self.actor['Birth Country'] == birth_country]
        avg_hight = filted['Height (Inches)'].mean()
        question = template.format(Birth_Country=birth_country)
        return question, avg_hight

    def q4(self):
        template = 'What is the total runtime of the {Genre} movie?'
        genre = self.movie['Genre'].sample(1).iloc[0]
        filted = self.movie[self.movie['Genre'] == genre]
        total = filted['Runtime'].sum()
        question = template.format(Genre=genre)
        return question, total


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
