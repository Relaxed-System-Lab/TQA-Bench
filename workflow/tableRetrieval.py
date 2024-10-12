import pandas as pd

import sys
sys.path.append('.')
from benchmarkUtils.jsTool import JS

if __name__ == '__main__':
    taskPath = 'dataset/task/tableQA/task.json'
    tasks = JS(taskPath).loadJS()
