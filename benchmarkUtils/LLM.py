import os
import tiktoken
import requests

import sys
sys.path.append('.')
from benchmarkUtils.database import DB


def gptCall():
    """
    这里注意要把模型推广到各种大语言模型中
    """
    pass

def countDBToken(dbPath, markdown=False):
    """
    dbPath: sqlite路径
    markdown: 是否转化成markdown格式, 否则转化为csv格式
    统计sqlite文件中表格转化成相应文件后的token大小
    """
    if not os.path.isfile(dbPath):
        return 0
    db = DB(dbPath)
    tabList = []
    for _, v in db.tables.items():
        tabStr = ''
        if not markdown:
            tabStr = v.to_csv(index=False)
        else:
            tabStr = v.to_markdown(index=False)
        tabList.append(tabStr)
    
    tkTool = tiktoken.get_encoding("cl100k_base")
    return len(tkTool.encode('\n\n'.join(tabList)))

if __name__ == '__main__':
    dbPath = '../SQLearn/dataset/movie.sqlite'
    tokSize = countDBToken(dbPath)
    print(tokSize)
