import os

from random import choice, choices
from re import template
import sys
sys.path.append('.')
from benchmarkUtils.database import DB
from symbolic.utils import choiceGen, stmtGen, numericalGen

class Olympics:
    def __init__(self, dbp) -> None:
        db = DB(dbp)
        self.tables = db.tables

        self.city = self.tables['city']
        self.games = self.tables['games']
        self.games_city = self.tables['games_city']
        self.medal = self.tables['medal']
        self.noc_region = self.tables['noc_region']
        self.person = self.tables['person']
        self.games_competitor = self.tables['games_competitor']
        self.person_region = self.tables['person_region']
        self.sport = self.tables['sport']
        self.event = self.tables['event']
        self.competitor_event = self.tables['competitor_event']

    def q0(self):
        template = 'Where is {full_name} from?'
        row = self.person_region.sample(1)
        person_id = row['person_id'].iloc[0]
        full_name = self.person[self.person['id'] == person_id]['full_name'].iloc[0]
        region_id = row['region_id'].iloc[0]
        region_name = self.noc_region[self.noc_region['id'] == region_id]['region_name'].iloc[0]
        question = template.format(full_name=full_name)

        rightIdx, choices = choiceGen(region_name,
                                      self.noc_region['region_name'])
        stmts = stmtGen(choices,
                        '{full_name} is from <unk>.'.format(full_name=full_name))
        return question, region_name, rightIdx, choices, stmts

    def q1(self):
        template = 'Which competitor is the highest in {games_name}?'
        games = self.games.sample(1)
        games_id = games['id'].iloc[0]
        games_name = games['games_name'].iloc[0]
        filted = self.games_competitor[self.games_competitor['games_id'] == games_id]
        filted = self.person[self.person['id'].isin(filted['id'])]
        max_val = filted['height'].max()
        full_name = filted[filted['height'] == max_val]['full_name'].to_list()
        question = template.format(games_name=games_name)

        rightIdx, choices = choiceGen(full_name, self.person['full_name'])
        stmts = stmtGen(choices,
                        'In {games_name}, <unk> is the highest.'.format(games_name=games_name))
        return question, full_name, rightIdx, choices, stmts

    def q2(self):
        template = 'How many competitors have heights larger or equal than {height}?'
        filted = self.person[self.person['id'].isin(self.games_competitor['id'])]
        height = filted['height'].sample(1).iloc[0]
        filted = self.person[self.person['height'] >= height]
        count = len(filted)
        question = template.format(height=height)

        rightIdx, choices = numericalGen(count)
        stmts = stmtGen(choices,
                        'There are <unk> competitors have heights larger or equal than {height}.'.format(height=height))
        return question, count, rightIdx, choices, stmts

    def q3(self):
        template = 'What is the average height of the competitors that took part in the games after {games_year}?'
        games_year = self.games.sample(1)['games_year'].iloc[0]
        games = self.games[self.games['games_year'] > games_year]
        filted = self.games_competitor[self.games_competitor['games_id'].isin(games['id'])]
        avg = filted['height'].mean()
        question = template.format(games_year=games_year)

        rightIdx, choices = numericalGen(avg)
        stmts = stmtGen(choices,
                        'The average height of the competitors that took part in the games after {games_year} is <unk>.'.format(games_year=games_year))
        return question, avg, rightIdx, choices, stmts

    def q4(self):
        template = 'What is the total height of all competitors that took part in {season} games?'
        season = self.games.sample(1)['season'].iloc[0]
        filted = self.games[self.games['season'] == season]
        games_competitor = self.games_competitor[self.games_competitor['games_id'].isin(filted['id'])]
        person = self.person[self.person['id'].isin(games_competitor['id'])]
        total = person['height'].sum()
        question = template.format(season=season)

        rightIdx, choices = numericalGen(total)
        stmts = stmtGen(choices,
                        'The total height of all competitors that took part in {season} games is <unk>.'.format(season=season))
        return question, total, rightIdx, choices, stmts

    def q5(self):
        template = 'Where is the {games_name} Olympics organized in?'
        row = self.games_city.sample(1)
        games_id = row['games_id'].iloc[0]
        city_id = row['city_id'].iloc[0]
        games_name = self.games[self.games['id'] == games_id]['games_name'].iloc[0]
        city_name = self.city[self.city['id'] == city_id]['city_name'].iloc[0]
        question = template.format(games_name=games_name)

        rightIdx, choices = choiceGen(city_name, self.city['city_name'])
        stmts = stmtGen(choices,
                        'The {games_name} Olympics organized in <unk>.'.format(games_name=games_name))
        return question, city_name, rightIdx, choices, stmts

    def q6(self):
        template = 'Which competitor has the most weight in {games_name}?'
        games = self.games.sample(1)
        games_id = games['id'].iloc[0]
        games_name = games['games_name'].iloc[0]
        filted = self.games_competitor[self.games_competitor['games_id'] == games_id]
        filted = self.person[self.person['id'].isin(filted['id'])]
        max_val = filted['weight'].max()
        full_name = filted[filted['weight'] == max_val]['full_name'].to_list()
        question = template.format(games_name=games_name)

        rightIdx, choices = choiceGen(full_name, self.person['full_name'])
        stmts = stmtGen(choices,
                        'In {games_name}, <unk> has the most weight.'.format(games_name=games_name))
        return question, full_name, rightIdx, choices, stmts

    def q7(self):
        template = 'How many competitors have weights larger or equal than {weight}?'
        filted = self.person[self.person['id'].isin(self.games_competitor['id'])]
        weight = filted['weight'].sample(1).iloc[0]
        filted = self.person[self.person['weight'] >= weight]
        count = len(filted)
        question = template.format(weight=weight)

        rightIdx, choices = numericalGen(count)
        stmts = stmtGen(choices,
                        'There are <unk> competitors have weights larger or equal than {weight}.'.format(weight=weight))
        return question, count, rightIdx, choices, stmts

    def q8(self):
        template = 'What is the average weight of the competitors that took part in the games after {games_year}?'
        games_year = self.games.sample(1)['games_year'].iloc[0]
        games = self.games[self.games['games_year'] > games_year]
        filted = self.games_competitor[self.games_competitor['games_id'].isin(games['id'])]
        avg = filted['weight'].mean()
        question = template.format(games_year=games_year)

        rightIdx, choices = numericalGen(avg)
        stmts = stmtGen(choices,
                        'The average weight of the competitors that took part in the games after {games_year} is <unk>.'.format(games_year=games_year))
        return question, avg, rightIdx, choices, stmts

    def q9(self):
        template = 'What is the total weight of all competitors that took part in {season} games?'
        season = self.games.sample(1)['season'].iloc[0]
        filted = self.games[self.games['season'] == season]
        games_competitor = self.games_competitor[self.games_competitor['games_id'].isin(filted['id'])]
        person = self.person[self.person['id'].isin(games_competitor['id'])]
        total = person['weight'].sum()
        question = template.format(season=season)

        rightIdx, choices = numericalGen(total)
        stmts = stmtGen(choices,
                        'The total weight of all competitors that took part in {season} games is <unk>.'.format(season=season))
        return question, total, rightIdx, choices, stmts

if __name__ == '__main__':
    dbRoot = 'dataset/optmizedScaledDB/8k/'
    dbn = 'olympics'
    dbp = os.path.join(dbRoot, dbn, f'{dbn}.sqlite')
    fi = Olympics(dbp)
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

