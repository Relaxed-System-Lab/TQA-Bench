import streamlit as st
import os

import sys
sys.path.append('.')
from benchmarkUtils.jsTool import JS
from benchmarkUtils.database import DB

jsPath = 'dataset/task/tableQA/task.json'
dataList = JS(jsPath).loadJS()

dataIdxs = list(range(len(dataList)))
idxSelected = st.selectbox('Index', dataIdxs)
data = dataList[int(idxSelected)]

dbName = data['database']
dbPath = os.path.join('dataset/scaledDB/16k', dbName, f'{dbName}.sqlite')
db = DB(dbPath)
tables = db.tables

st.write(data['question'])
st.write(f"```python\n{data['code']}\n```")
st.write(data['choices'])

with st.form('annotation'):
    anno = data.get('annotation', '')
    newAnno = st.text_input('Annotation: If the question is ambugous, annotate 0 in front of it. "item", "sum", "average", "count".', anno)
    formBut = st.form_submit_button('update')

if formBut:
    data['annotation'] = newAnno
    JS(jsPath).newJS(dataList)
    st.rerun()

for k, v in tables.items():
    st.header(k)
    st.write(v)
