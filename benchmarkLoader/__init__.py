import os
from torch.utils.data import Dataset

import sys
sys.path.append('.')
from benchmarkUtils.database import DB

scaledRoot = 'dataset/scaledDB'

with open('benchmarkLoader/prompts/singleChoicePrompt.txt', 'r') as f:
    singlePrompt = f.read()

with open('benchmarkLoader/prompts/multiChoicePrompt.txt', 'r') as f:
    multiPrompt = f.read()

with open('benchmarkLoader/prompts/batchedSingleChoicePrompt.txt', 'r') as f:
    batchedSinglePrompt = f.read()

class BenchmarkDataset(Dataset):
    def __init__(self, scale, markdown=True):
        self.scale = scale
        self.markdown = markdown
        self.dbRoot = os.path.join(scaledRoot, scale)
        self.maps = 'A B C D E'.split()

    def loadDB(self, dbn):
        dbp = os.path.join(self.dbRoot, dbn, f'{dbn}.sqlite')
        return DB(dbp)
