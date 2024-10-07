import re
import io
import pandas as pd
import numpy as np

import sys
sys.path.append('.')

class HiddenPrints(io.StringIO):
    def write(self, txt):
        pass

def codeExec(code, varDict):
    printCount = len(re.findall(r'\bprint\s*\(', code))
    if printCount != 1:
        raise IndexError # print数超过1个
    # 匹配所有的 print 函数调用内容
    print_calls = re.findall(r'print\s*\((.*?)\)', code, re.DOTALL)

    # 匹配变量名的正则表达式
    variable_pattern = r'\b[a-zA-Z_]\w*\b'

    # 保存所有匹配到的变量
    variables = []

    for call in print_calls:
        # 去掉字符串部分 (用正则匹配并替换为'')
        no_strings = re.sub(r'".*?"|\'[^\']*\'|f\".*?\"', '', call)
        
        # 查找变量名
        variables += re.findall(variable_pattern, no_strings)

    # 去除重复的变量名
    unique_variables = list(set(variables))

    if len(unique_variables) != 1:
        raise ValueError # 值数超过1个

    varName = unique_variables[0]
    original_stdout = sys.stdout
    sys.stdout = HiddenPrints()
    try:
        exec(code, varDict)
        sys.stdout = original_stdout
        if type(varDict[varName]) in [pd.DataFrame, pd.Series, list, tuple]:
            raise TypeError
        if varDict[varName] in [None, np.nan]:
            raise ValueError
        return varDict[varName]
    except:
        sys.stdout = original_stdout
        raise RuntimeError # 执行错误
