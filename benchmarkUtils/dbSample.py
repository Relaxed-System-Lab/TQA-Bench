import os
from os.path import isfile
import shutil
import multiprocessing
import sys

from tqdm import tqdm
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
    dstJSPath = os.path.join(dstRoot, 'sampleInfo.json')

    # 对原始数据库计数
    originalTokenSize = countDBToken(srcPath, markdown)
    if originalTokenSize < minToken:
        # 如果原始表都不足minToken则去掉
        return False

    os.makedirs(dstRoot, exist_ok=True)
    if originalTokenSize <= maxToken:
        # 在区间内则直接复制
        shutil.copy2(srcPath, dstDBPath)
        JS(dstJSPath).newJS({
            'markdown': markdown,
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
                'markdown': markdown,
                'token': tokenSize,
                'sample': rp
            })
            return True
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
            JS(dstJSPath).newJS({
                'markdown': markdown,
                'token': tokenSize,
                'sample': cp
            })
            return True
    if os.path.isfile(dstDBPath):
        os.remove(dstDBPath)
    return True

def multiProcessSample(dbRoot, sampRoot, minToken, maxToken, initRow=32, markdown=False, processes=64, maxSize=1024):
    """
    dbRoot: 数据库的根目录
    sampRoot: 采样后需要放置的目录
    minToken: 采样后数据库最低的token数
    maxToken: 最高token数
    initRow: 初始的采样大小
    markdown: 是否使用markdown来转化表格
    processes: 使用多少进程来进行采样
    maxSize: 采样数据库的大小上限 (MB)
    """
    os.makedirs(sampRoot, exist_ok=True)
    dbNames = os.listdir(dbRoot)

    pBar = tqdm(total = len(dbNames))
    pool = multiprocessing.Pool(processes=processes)
    for dbn in dbNames:
        dbp = os.path.join(dbRoot, dbn, f'{dbn}.sqlite')
        sz = os.path.getsize(dbp) / 2**20
        if sz > maxSize:
            # 先不采样超过1G的, 太慢了
            pBar.update()
            continue
        pool.apply_async(tokenBasedSample, (
            dbp,
            sampRoot,
            minToken,
            maxToken,
            initRow,
            markdown
        ), callback=lambda _: pBar.update())
    pool.close()
    pool.join()
    pBar.close()

    # 对于采样失败的, 需要将其目录移除
    for dbn in dbNames:
        dbr = os.path.join(sampRoot, dbn)
        dbp = os.path.join(sampRoot, dbn, f'{dbn}.sqlite')
        jsp = os.path.join(sampRoot, dbn, 'sampleInfo.json')
        if not os.path.isfile(jsp) and os.path.isdir(dbr):
            shutil.rmtree(dbr)
        if os.path.isfile(dbp) and not DB.foreignKeyCheck(dbp):
            shutil.rmtree(dbr)

if __name__ == '__main__':
    dbRoot = 'dataset/workflowDB'
    sampRoot = 'dataset/sampleDB'
    multiProcessSample(
        dbRoot,
        sampRoot,
        4 * 1024,
        6 * 1024,
        32,
        False,
        64
    )
