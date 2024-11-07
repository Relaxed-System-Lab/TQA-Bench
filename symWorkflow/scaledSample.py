import os

import shutil
import sys
sys.path.append('.')
from benchmarkUtils.LLM import countDBToken
from benchmarkUtils.database import DB
from benchmarkUtils.jsTool import JS

from symbolic import dataDict

def tokenBasedSample(
    srcPath:str,
    dstDBPath:str,
    minToken:int,
    maxToken:int,
    initRow:int=32,
    markdown:bool=False
    ):
    """
    srcPath: 待采样数据表路径
    dstDBPath: 采样后保存sqlite路径
    minToken: token数的最小值
    maxToken: token数的最大值
    markdown: 是否采用markdown格式
    对于srcRoot内的所有数据表进行采样, 保存在sampRoot中, 保证sampRoot中每个sqlite表转化为csv字符串后, token数要在minToken和maxToken之间
    """
    if os.path.isfile(dstDBPath):
        return False

    # 对原始数据库计数
    originalTokenSize = countDBToken(srcPath, markdown)
    if originalTokenSize < minToken:
        # 如果原始表都不足minToken则去掉
        return False

    if originalTokenSize <= maxToken:
        # 在区间内则直接复制
        shutil.copy2(srcPath, dstDBPath)
        return {
            'markdown': markdown,
            'token': originalTokenSize,
            'sample': -1 # -1代表没有做采样, 而是直接复制的
        }

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
            return {
                'markdown': markdown,
                'token': tokenSize,
                'sample': rp
            }
        else:
            # 大于了, 要用2分法了
            break
        lastTokenSize = tokenSize

    lp = rp // 2
    cp = -1
    while cp != (lp + rp) // 2:
        cp = (lp + rp) // 2
        db.sample(dstDBPath, cp)
        tokenSize = countDBToken(dstDBPath)
        if tokenSize < minToken:
            lp = cp + 1
        elif tokenSize > maxToken:
            rp = cp - 1
        else:
            return {
                'markdown': markdown,
                'token': tokenSize,
                'sample': cp
            }
    if os.path.isfile(dstDBPath):
        os.remove(dstDBPath)
    return False

def scaledSample(
    sampleCount,
    maxTry,
    srcDB,
    dstPath,
    minToken,
    maxToken,
    initRow,
    markdown
    ):
    os.makedirs(dstPath, exist_ok=True)
    for i in range(sampleCount):
        dstDB = os.path.join(dstPath, f'{i}.sqlite')
        if os.path.isfile(dstDB):
            continue
        for _ in range(maxTry):
            res = tokenBasedSample(srcDB, dstDB, minToken, maxToken, initRow, markdown)
            if res != False:
                break

scaleDict = {
    '8k': (4, 6),
    '32k': (16, 24),
    '64k': (32, 48),
    '128k': (64, 96)
}

if __name__ == '__main__':
    for k, v in scaleDict.items():
        for dbn in dataDict.keys():
            scaledSample(10,
                        8,
                        f'symDataset/scaledDB/csv128k/{dbn}/{dbn}.sqlite',
                        f'symDataset/scaledDB/{k}/{dbn}',
                        v[0] * 1024,
                        v[1] * 1024,
                        32,
                        True
                        )
