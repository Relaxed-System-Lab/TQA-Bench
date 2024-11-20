import streamlit as st

import sys
sys.path.append('.')
from dbMerge import ResultAnalysis

if not st.session_state.get("password_correct", False):
    st.switch_page('server.py')

ra = ResultAnalysis('tmp.sqlite')
tables = ra.count(5, 14)

if st.button('Update Data'):
    ra.mergeTables('symDataset/results/TableQA/4o.sqlite')

if tables:
    for k, v in tables.items():
        st.header(k)
        st.write(v)
