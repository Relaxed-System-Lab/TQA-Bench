import random
import pandas as pd

def corrGen(corr):
    if abs(corr) < 0.1:
        choices = [-0.1, corr, 0.1, 0.2]
        random.shuffle(choices)
        return choices.index(corr), choices
    a = []
    if abs(corr) > 0.75:
        a = [0.25, 0.5, 0.75]
    elif abs(corr) > 0.5:
        a = [0.33, 0.66, 1.32]
    elif abs(corr) > 0.25:
        a = [0.5, 1.5, 2]
    else:
        a = [2, 3, 4]
    choices = [item * corr for item in a]
    choices.append(corr)
    random.shuffle(choices)
    return choices.index(corr), choices


def choiceGen(item, series):
    if type(series) is pd.Series:
        series = series.drop_duplicates().to_list()
    sz = len(series)
    choices = random.sample(series, min(4, sz))
    while len(choices) < 4:
        for item in [0, None, 'Unknown']:
            if len(choices) >= 4:
                break
            choices.append(item)
    if type(item) == list:
        choices = [[i] for i in choices]
    if item not in choices:
        choices = [item] + choices[:3]
    random.shuffle(choices)
    rightIdx = choices.index(item)
    return rightIdx, choices

def formSeries(series):
    if len(series) == 0:
        return ''
    elif len(series) == 1:
        return series[0]
    series = [str(item) for item in series]
    formalStmt = ', '.join(series[:-1])
    return f'{formalStmt}, and {series[-1]}'

def stmtGen(series, template):
    if type(series[0]) is list:
        series = [formSeries(item) for item in series]
    return [template.replace('<unk>', str(item)) for item in series]

def numericalGen(val):
    if val == None or val == 0:
        return 1, [-1, val, 1, 2]
    rate = [0.25, 2, 3]
    choices = [val * item for item in rate]
    if type(val) == int:
        choices = [int(item) for item in choices]
    choices = [val] + choices
    random.shuffle(choices)
    rightIdx = choices.index(val)
    return rightIdx, choices
