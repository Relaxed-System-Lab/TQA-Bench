import os
from tqdm import tqdm
from os.path import exists, isfile
import shutil

import sys

from pandas.core.computation.parsing import tokenize_string
sys.path.append('.')
from benchmarkUtils.database import DB
from benchmarkUtils.LLM import countDBToken
from benchmarkUtils.jsTool import JS


def tokenBasedSample(
    srcPath:str,
    dstPath:str,
    minToken:int,
    maxToken:int,
    initRow:int=32,
    markdown:bool=False
    ):
    """
    srcPath: 待采样数据表路径
    dstPath: 采样后保存路径
    minToken: token数的最小值
    maxToken: token数的最大值
    markdown: 是否采用markdown格式
    对于srcRoot内的所有数据表进行采样, 保存在sampRoot中, 保证sampRoot中每个sqlite表转化为csv字符串后, token数要在minToken和maxToken之间
    """

    # 从srcPath中提取文件名称fn, 以及具体的数据库名称dbn
    fn = os.path.basename(srcPath)
    dbn, _ = os.path.splitext(fn)
    
    # 目标目录下需要新建多个文件
    dstRoot = os.path.join(dstPath, dbn)
    dstDBPath = os.path.join(dstRoot, fn)
    dstJSPath = os.path.join(dstRoot, fn)

    # 对原始数据库计数
    originalTokenSize = countDBToken(srcPath, markdown)
    print(originalTokenSize)
    if originalTokenSize < minToken:
        # 如果原始表都不足minToken则去掉
        return False

    os.makedirs(dstRoot, exist_ok=True)
    if originalTokenSize <= maxToken:
        # 在区间内则直接复制
        shutil.copy2(srcPath, dstDBPath)
        JS(dstJSPath).newJS({
            'token': originalTokenSize,
            'sample': -1 # -1代表没有做采样, 而是直接复制的
        })
        return True

    db = DB(srcPath, initTables=False)
    rp = initRow
    lastTokenSize = 0
    tokenSize = 0
    while True:
        db.sample(dstDBPath, rp)
        tokenSize = countDBToken(dstDBPath)
        if tokenSize < minToken:
            if tokenSize <= lastTokenSize:
                # 当上一次采样甚至比这次要多的时候, 表明采样到了上限, 不会再增加了
                return False
            rp *= 2
        elif tokenSize <= maxToken:
            JS(dstJSPath).newJS({
                'token': tokenSize,
                'sample': rp
            })
            return True
        else:
            # 大于了, 要用2分法了
            break
        print(rp)
        lastTokenSize = tokenSize

    lp = rp // 2
    cp = -1
    while cp != (lp + rp) // 2:
        cp = (lp + rp) // 2
        print(cp)
        db.sample(dstDBPath, cp)
        tokenSize = countDBToken(dstDBPath)
        if tokenSize < minToken:
            lp = cp + 1
        elif tokenSize > maxToken:
            rp = cp - 1
        else:
            JS(dstJSPath).newJS({
                'token': tokenSize,
                'sample': cp
            })
            return True
    if os.path.isfile(dstDBPath):
        os.remove(dstDBPath)
    return True


if __name__ == '__main__':
    dbRoot = 'dataset/workflowDB'
    sampRoot = 'dataset/sampleDB'
    os.makedirs(sampRoot, exist_ok=True)
    dbNames = os.listdir(dbRoot)
    for dbn in tqdm(dbNames):
        print(dbn)
        dbp = os.path.join(dbRoot, dbn, f'{dbn}.sqlite')
        tokenBasedSample(
            dbp,
            sampRoot,
            32 * 1024,
            64 * 1024
        )
