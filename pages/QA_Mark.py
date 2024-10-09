import os
import streamlit as st

import sys

sys.path.append('.')
# from benchmarkUtils.stUtil import *
from benchmarkUtils.stUtil import FrontEndDataset
from benchmarkUtils.jsTool import JS
from benchmarkUtils.database import DB
from workflow import qaRoot, scaleRoot


srcPath = os.path.join(qaRoot, 'valid')
jsNames  = [item for item in os.listdir(srcPath) if item.endswith('.json')]

selectedJS = st.selectbox('Please select a json file to read', jsNames)
selectedJSPath = os.path.join(srcPath, str(selectedJS))

# 要用一个索引号来维护prev和next
if 'idx' not in st.session_state:
    st.session_state.idx = 0

qaList = JS(selectedJSPath).loadJS()

st.session_state.idx = (st.session_state.idx + len(qaList)) % len(qaList)

col1, col2 = st.columns([1, 1])
with col1:
    if st.button('Prev', use_container_width=True):
        st.session_state.idx = (st.session_state.idx + len(qaList) - 1) % len(qaList)
with col2:
    if st.button('Next', use_container_width=True, type='primary'):
        st.session_state.idx = (st.session_state.idx + 1) % len(qaList)
currIdx = st.selectbox('Please select a QA', list(range(len(qaList))), st.session_state.idx)

if currIdx != st.session_state.idx:
    st.session_state.idx = currIdx

with st.form('Edit Question and Choices', clear_on_submit=True):
    q = st.text_area('Question', qaList[st.session_state.idx]['question'])
    a = ['' for _ in range(4)]
    a = qaList[st.session_state.idx].get('choices', [])
    a = a + ['' for _ in range(4 - len(a))]
    a[0] = st.text_input('answer1', a[0])
    a[1] = st.text_input('answer2', a[1])
    a[2] = st.text_input('answer3', a[2])
    a[3] = st.text_input('answer4', a[3])
    fCol1, fCol2 = st.columns([1, 1])
    with fCol1:
        if st.form_submit_button('Update', use_container_width=True):
            qaList[st.session_state.idx]['question'] = q
            a = [item for item in a if item != '']
            if len(a) > 0:
                qaList[st.session_state.idx]['choices'] = a
            else:
                del qaList[st.session_state.idx]['choices']
            JS(selectedJSPath).newJS(qaList)
            st.rerun() # don't forget to re-render the page
    with fCol2:
        if st.form_submit_button('Delete', use_container_width=True):
            del qaList[st.session_state.idx]
            JS(selectedJSPath).newJS(qaList)
            st.rerun() # don't forget to re-render the page

st.write(qaList[st.session_state.idx])

dbn = qaList[st.session_state.idx]['database']
st.title(dbn)
dbp = os.path.join(scaleRoot, '16k', dbn, f'{dbn}.sqlite')
FrontEndDataset(dbp).renderDataset()
