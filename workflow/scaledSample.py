import os

import sys
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
        '8k': (4, 6)
    }
    ):
    """
    sampRoot: 保存不同规模的采样结果, 需要从最大依次采样到最小
    scaledDict: key是采样规模的字符串, value是区间 (单位是k) , 同时要规模从大到小排列
    会从srcRoot中采样所有的表格, 并将结果存到sampRoot/{maxScale}中, 后面都是从上一级scale采样得到下一级
    """
    refRoot = srcRoot
    for k, v in scaledDict.items():
        currRoot = os.path.join(sampRoot, k)
        multiProcessSample(
            refRoot,
            currRoot,
            v[0] * 1024, # 别忘了k
            v[1] * 1024, # 转化k
            32, # 初始采样行为32
            False, # 为了保证序列化后能给到相应规模的模型, 这里保守用更长序列化的方案
            64, # 使用64个process来进行采样
            1024 # 跳过超过1GB的sqlite文件
        )
        refRoot = currRoot

if __name__ == '__main__':
    scaledSample(
        'dataset/workflowDB',
        'dataset/scaledDB'
    )
