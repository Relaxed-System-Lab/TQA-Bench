import streamlit as st
import sys
sys.path.append('.')

scaledDataset = 'symDataset/scaledDB/symDataset.zip'
taskDataset = 'symDataset/tasks/tasks.zip'

st.write('Download symbolic dataset.')
with open(scaledDataset, 'rb') as f:
    st.download_button('Download scaledDB', f, file_name='symDataset.zip')
st.write('Download task dataset.')
with open(taskDataset, 'rb') as f:
    st.download_button('Download tasks', f, file_name='tasks.zip')
