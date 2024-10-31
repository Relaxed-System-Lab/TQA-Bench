import os
import streamlit as st

import sys
sys.path.append('.')
from benchmarkUtils.jsTool import JS
from benchmarkUtils.database import DB

taskPath = 'dataset/task/tableQA/task.json'
taskList = JS(taskPath).loadJS()
choicesMap = 'A B C D E'.split()

logPath = 'results/qa/'
jsNames = os.listdir(logPath)

jsNames.sort(key=lambda x:int(x[3:].split('_')[0]))

jsSelected = st.selectbox('File Names', jsNames)
jsPath = os.path.join(logPath, jsSelected)
dic = JS(jsPath).loadJS()
with st.form('annotation'):
    anno = dic.get('annotation', '')
    newAnno = st.text_input('annotation', anno)
    formBut = st.form_submit_button('update')

if formBut:
    dic['annotation'] = newAnno
    JS(jsPath).newJS(dic)
    st.rerun()

idx = int(jsSelected[3:].split('_')[0])
task = taskList[idx]

question = task['question']
dbName = task['database']
code = task['code']
rightIdx = task['rightIdx']['16k']
choice = choicesMap[rightIdx]
answer = task['choices'][rightIdx]
annotation = task.get('annotation')
st.write(question)
st.write(f'{choice}) {answer}')
st.write(f'```python\n{code}\n```')
st.write(annotation)

st.write(dic)

dbPath = os.path.join('dataset/scaledDB/16k', dbName, f'{dbName}.sqlite')
tables = DB(dbPath).tables
for k, v in tables.items():
    st.header(k)
    st.write(v)

