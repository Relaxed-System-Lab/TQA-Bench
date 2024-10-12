import os
from torch.utils.data import Dataset

import sys
sys.path.append('.')
from benchmarkUtils.database import DB

scaledRoot = 'dataset/scaledDB'

class BenchmarkDataset(Dataset):
    def __init__(self, scale, markdown=True):
        self.scale = scale
        self.markdown = markdown
        self.dbRoot = os.path.join(scaledRoot, scale)
        self.maps = 'A B C D E'.split()

    def loadDB(self, dbn):
        dbp = os.path.join(self.dbRoot, dbn, f'{dbn}.sqlite')
        return DB(dbp)
