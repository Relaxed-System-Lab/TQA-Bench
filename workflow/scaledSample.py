import os

import sys

from pandas.core.frame import maybe_droplevels
sys.path.append('.')

from benchmarkUtils.dbSample import multiProcessSample

def scaledSample(
    srcRoot:str,
    sampRoot:str,
    scaledDict:dict={
        '128k': (64, 96),
        '64k': (32, 48),
        '32k': (16, 24),
        '16k': (8, 12),
        '8k': (2, 6)
    },
    markdown=True
    ):
    """
    srcRoot: 原始数据集的结果
    sampRoot: 保存不同规模的采样结果, 需要从最大依次采样到最小
    scaledDict: key是采样规模的字符串, value是区间 (单位是k) , 同时要规模从大到小排列
    markdown: 是否采用markdown作为序列化方案
    会从srcRoot中采样所有的表格, 并将结果存到sampRoot/{maxScale}中, 后面都是从上一级scale采样得到下一级
    """
    refRoot = srcRoot
    if markdown:
        print('Preparing Dataset for MarkDown sampling...')
        """
        在使用markdown时, 必须先用CSV序列化方案把规模降下来, 否则速度会非常慢
        """
        maxKey = list(scaledDict.keys())[0]
        mdRoot = os.path.join(sampRoot, f'csv{maxKey}')
        lp = scaledDict[maxKey][0] * 2
        rp = scaledDict[maxKey][1] * 2
        multiProcessSample(
            srcRoot,
            mdRoot,
            lp * 1024, # 别忘了k
            rp * 1024, # 转化k
            32, # 初始采样行为32
            False, # 这里一定要用CSV而非markdown, 来实现更快的采样
            64, # 使用64个process来进行采样
            1024 # 跳过超过1GB的sqlite文件
        )
        refRoot = mdRoot
    print('Scaled sampling...')
    for k, v in scaledDict.items():
        print(f'{k} is sampling...')
        currRoot = os.path.join(sampRoot, k)
        multiProcessSample(
            refRoot,
            currRoot,
            v[0] * 1024, # 别忘了k
            v[1] * 1024, # 转化k
            32, # 初始采样行为32
            markdown, # 这里与提供的参数保持一致
            64, # 使用64个process来进行采样
            1024 # 跳过超过1GB的sqlite文件
        )
        refRoot = currRoot
        print(f'{k} finished.')

if __name__ == '__main__':
    scaledSample(
        'dataset/workflowDB',
        'dataset/optmizedScaledDB'
    )
