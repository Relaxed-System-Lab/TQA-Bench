import os
from urllib.parse import quote_plus
import pandas as pd

import sys
sys.path.append('.')
from benchmarkUtils.database import DB
from symbolic.utils import choiceGen, corrGen, stmtGen, numericalGen


class MusicTracker:
    retrieval = [
        ['torrents'],
        ['torrents', 'tags'],
        ['torrents', 'tags'],
        ['torrents'],
        ['torrents', 'tags'],
        ['tags'],
        ['torrents', 'tags'],
        ['tags'],
        ['torrents', 'tags'],
        ['torrents', 'tags']
    ]
    def __init__(self, dbp) -> None:
        db = DB(dbp)
        self.tables = db.tables

        self.torrents = self.tables['torrents']
        self.tags = self.tables['tags']
        self.merged_df = pd.merge(self.torrents, self.tags, left_on='id', right_on='id')


    def q0(self):
        template = 'What is the release type of torrent id {id}?'
        row = self.merged_df.sample(1)
        id = row['id'].iloc[0]
        release_type = row['releaseType'].iloc[0]
        question = template.format(id=id)

        rightIdx, choices = choiceGen(release_type, self.merged_df['releaseType'])
        stmts = stmtGen(choices,
                        'The release type of torrent id {id} is <unk>'.format(id=id))
        return question, release_type, rightIdx, choices, stmts

    def q1(self):
        template = 'Which release type contains most {tag} tag?'
        tag = self.merged_df['tag'].sample(1).iloc[0]
        filted = self.merged_df[self.merged_df['tag'] == tag]
        max_count = filted['releaseType'].value_counts()
        max_val = max_count.max()
        filted_series = max_count[max_count == max_val]
        items = filted_series.index.to_list()
        question = template.format(tag=tag)

        rightIdx, choices = choiceGen(items, self.merged_df['releaseType'])
        stmts = stmtGen(choices,
                        'The release type <unk> contains most {tag} tag.'.format(tag=tag))
        return question, items, rightIdx, choices, stmts

    def q2(self):
        template = 'How many torrents are relesed in {releaseType} and with {tag} tag?'
        releaseType = self.merged_df['releaseType'].sample(1).iloc[0]
        filted = self.merged_df[self.merged_df['releaseType'] == releaseType]
        tag = filted['tag'].sample(1).iloc[0]
        filted = filted[filted['tag'] == tag]
        count = len(filted)
        question = template.format(releaseType=releaseType, tag=tag)

        rightIdx, choices = numericalGen(count)
        stmts = stmtGen(choices,
                        'There are <unk> torrents are relesed in {releaseType} and with {tag} tag.'.format(releaseType=releaseType, tag=tag))
        return question, count, rightIdx, choices, stmts

    def q3(self):
        template = 'What is the average snatch of {releaseType}?'
        releaseType = self.merged_df['releaseType'].sample(1).iloc[0]
        filted = self.merged_df[self.merged_df['releaseType'] == releaseType]
        avg = filted['totalSnatched'].mean()
        question = template.format(releaseType=releaseType)

        rightIdx, choices = numericalGen(avg)
        stmts = stmtGen(choices,
                        'The average snatch of {releaseType} is <unk>.'.format(releaseType=releaseType))
        return question, avg, rightIdx, choices, stmts

    def q4(self):
        template = 'What is the total snatch with {tag} tag?'
        tag = self.merged_df['tag'].sample(1).iloc[0]
        filted = self.merged_df[self.merged_df['tag'] == tag]
        total = filted['totalSnatched'].sum()
        question = template.format(tag=tag)

        rightIdx, choices = numericalGen(total)
        stmts = stmtGen(choices,
                        'The total snatch with {tag} tag is <unk>.'.format(tag=tag))
        return question, total, rightIdx, choices, stmts

    def q5(self):
        template = 'What is the tag of the id {id}?'
        row = self.tags.sample(1)
        id = row['id'].iloc[0]
        tag = row['tag'].iloc[0]
        question = template.format(id=id)

        rightIdx, choices = choiceGen(tag, self.tags['tag'])
        stmts = stmtGen(choices,
                        'The tag of the id {id} is <unk>.'.format(id=id))
        return question, tag, rightIdx, choices, stmts

    def q6(self):
        template = 'Which tag contains most release type {releaseType}?'
        releaseType = self.merged_df['releaseType'].sample(1).iloc[0]
        filted = self.merged_df[self.merged_df['releaseType'] == releaseType]
        max_count = filted['tag'].value_counts()
        max_val = max_count.max()
        filted_series = max_count[max_count == max_val]
        items = filted_series.index.to_list()
        question = template.format(releaseType=releaseType)

        rightIdx, choices = choiceGen(items, self.tags['tag'])
        stmts = stmtGen(choices,
                        'The tag <unk> contains most release type {releaseType}.'.format(releaseType=releaseType))
        return question, items, rightIdx, choices, stmts

    def q7(self):
        template = 'How many torrents are in {tag} tag?'
        tag = self.merged_df['tag'].sample(1).iloc[0]
        filted = self.merged_df[self.merged_df['tag'] == tag]
        count = len(filted)
        question = template.format(tag=tag)

        rightIdx, choices = numericalGen(count)
        stmts = stmtGen(choices,
                        'There are <unk> torrents are in {tag} tag'.format(tag=tag))
        return question, count, rightIdx, choices, stmts

    def q8(self):
        template = 'What is the average snatch of {tag}?'
        tag = self.merged_df['tag'].sample(1).iloc[0]
        filted = self.merged_df[self.merged_df['tag'] == tag]
        avg = filted['totalSnatched'].mean()
        question = template.format(tag=tag)

        rightIdx, choices = numericalGen(avg)
        stmts = stmtGen(choices,
                        'The average snatch of {tag} is <unk>.'.format(tag=tag))
        return question, avg, rightIdx, choices, stmts

    def q9(self):
        template = 'What is the total snatch with release type {releaseType}?'
        releaseType = self.merged_df['releaseType'].sample(1).iloc[0]
        filted = self.merged_df[self.merged_df['releaseType'] == releaseType]
        total = filted['totalSnatched'].sum()
        question = template.format(releaseType=releaseType)

        rightIdx, choices = numericalGen(total)
        stmts = stmtGen(choices,
                        'The total snatch with release type {releaseType} is <unk>.'.format(releaseType=releaseType))
        return question, total, rightIdx, choices, stmts

    def q10(self):
        template = 'How many total snatched are id {id0} more than id {id1}?'
        rows = self.torrents.sample(2)
        id0 = rows['id'].iloc[0]
        id1 = rows['id'].iloc[1]
        diff = rows['totalSnatched'].iloc[0] - rows['totalSnatched'].iloc[1]
        question = template.format(id0=id0, id1=id1)

        rightIdx, choices = numericalGen(diff)
        return question, diff, rightIdx, choices

    def q11(self):
        template = 'How many average total snatched are releaseType {type0} more than {type1}?'
        types = self.torrents['releaseType'].drop_duplicates().sample(2)
        type0 = types.iloc[0]
        type1 = types.iloc[1]
        diff = self.torrents[self.torrents['releaseType'] == type0]['totalSnatched'].mean() - self.torrents[self.torrents['releaseType'] == type1]['totalSnatched'].mean()
        question = template.format(type0=type0, type1=type1)

        rightIdx, choices = numericalGen(diff)
        return question, diff, rightIdx, choices

    def q12(self):
        template = 'What is the correlation between total snatched and group year of music that are {releaseType}?'
        releaseType = self.torrents['releaseType'].sample(1).iloc[0]
        filted = self.torrents[self.torrents['releaseType'] == releaseType]
        corr = filted['totalSnatched'].corr(filted['groupYear'])
        question = template.format(releaseType=releaseType)

        rightIdx, choices = corrGen(corr)
        return question, corr, rightIdx, choices

    def q13(self):
        template = 'What is the correlation between total snatched and group year of music that are with tag {tag}?'
        tag = self.tags['tag'].sample(1).iloc[0]
        ids = self.tags[self.tags['tag'] == tag]['id']
        filted = self.torrents[self.torrents['id'].isin(ids)]
        corr = filted['totalSnatched'].corr(filted['groupYear'])
        question = template.format(tag=tag)

        rightIdx, choices = corrGen(corr)
        return question, corr, rightIdx, choices


if __name__ == '__main__':
    dbRoot = 'symDataset/scaledDB/8k/'
    dbn = 'music_tracker'
    dbp = os.path.join(dbRoot, dbn, '0.sqlite')
    fi = MusicTracker(dbp)
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
