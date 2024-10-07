import os
import tiktoken
import requests
from datetime import datetime
from uuid import uuid4

import sys
sys.path.append('.')
from benchmarkUtils.database import DB
from benchmarkUtils.jsTool import JS

def gptCall(model,
            prompt,
            logStart="",
            logPath="logs",
            proxies={
                'http': 'socks5://127.0.0.1:1080',
                'https': 'socks5://127.0.0.1:1080',
            }, # 代理字典, 这里默认使用1080端口的sock5代理
            OPENAI_API_KEY=None,
            otherInfo={}
            ):
    """
    model: gpt模型, 包括gpt-4, gpt-4o, gpt-4o-mini等
    prompt: 提示词
    logStart: 日志文件开头, 建议不要插入 `_` 在其中
    logPath: 日志文件地址, 若不存在则自动创建
    proxies: requests使用的代理地址, 默认是在1080端口的socks5代理
    OPENAI_API_KEY: openai的key, 如果保持None则读取环境变量
    """
    os.makedirs(logPath, exist_ok=True)
    if OPENAI_API_KEY is None:
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }
    bodies = {
        "model": model,
        "messages": [
        {
            "role": "user",
            "content": [
            {
                "type": "text",
                "text": prompt
            }
            ]
        }
        ],
    }
    msg = None
    try:
        msg = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=bodies, proxies=proxies).json()
        msg = msg['choices'][0]['message']['content']
    except Exception as e:
        print(e)
        msg = f'error: {e}\n' + str(msg)
    otherInfo.update({"model": model, "prompt": prompt, "message": msg})
    fileName = datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + "_" + str(uuid4()) + ".json"
    if logStart != "":
        fileName = logStart + "_" + fileName
    filePath = os.path.join(logPath, fileName)
    JS(filePath).newJS(otherInfo)
    return msg

def countDBToken(dbPath, markdown=False):
    """
    dbPath: sqlite路径
    markdown: 是否转化成markdown格式, 否则转化为csv格式
    统计sqlite文件中表格转化成相应文件后的token大小
    """
    if not os.path.isfile(dbPath):
        return 0
    db = DB(dbPath)
    dbStr = db.defaultSerialization(markdown=markdown)
    tkTool = tiktoken.get_encoding("cl100k_base")
    return len(tkTool.encode(dbStr))

if __name__ == '__main__':
    dbp = 'dataset/sampleDB/movie/movie.sqlite'
    logPath = 'dataset/log/tmp/'
    db = DB(dbp)
    dbStr = db.defaultSerialization(markdown=True)
    prompt = f'Please summarize the important information in the following tables.\n\n{dbStr}'
    res = gptCall('gpt-4o-mini', prompt, logPath=logPath)
    print(res)
