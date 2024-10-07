import streamlit as st
import json
import os

import sys
sys.path.append('.')
from benchmarkUtils.jsTool import JS

# if not st.session_state.get("password_correct", False):
#     st.switch_page('server.py')

promptPath = 'workflow/templates.json'

def renderPrompt(promptPath):
    with open(promptPath, 'r') as f:
        dic = json.load(f)
    selectdPrompt = st.selectbox('Select a Prompt', ['+'] + list(dic.keys()))
    return dic, selectdPrompt

dic, selectedPrompt = renderPrompt(promptPath)

with st.form('prompt'):
    val = dic.get(selectedPrompt, '')
    tit = st.text_input('Prompt Title', selectedPrompt if selectedPrompt != '+' else '')
    val = st.text_area('Prompt Template', val, height=512)
    if selectedPrompt == '+':
        addBut = st.form_submit_button('Add', use_container_width=True)
        if addBut:
            dic[tit] = val
            JS(promptPath).newJS(dic)
            st.rerun()
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            addBut = st.form_submit_button('Add', use_container_width=True)
        with c2:
            editBut = st.form_submit_button('Edit', use_container_width=True)
        with c3:
            delBut = st.form_submit_button('Delete', type='primary', use_container_width=True)
        if addBut:
            dic[tit] = val
            JS(promptPath).newJS(dic)
            st.rerun()
        if editBut:
            dic[selectedPrompt] = val
            # del dic[selectedPrompt]
            JS(promptPath).newJS(dic)
            st.rerun()
        if delBut:
            del dic[selectedPrompt]
            JS(promptPath).newJS(dic)
            st.rerun()
