import streamlit as st
import sys
sys.path.append('.')
from benchmarkLoader.tableQALoader import TableQADataset
from benchmarkLoader.tableFVLoader import TableFVDataset
from benchmarkLoader.retrievalLoader import RetrievalDataset
from benchmarkLoader.cpaLoader import CPADataset
from benchmarkLoader.ctaLoader import CTADataset
from benchmarkLoader.emLoader import EMDataset

dsDict = {
    'qa': TableQADataset,
    'fv': TableFVDataset,
    'ret': RetrievalDataset,
    'cpa': CPADataset,
    'cta': CTADataset,
    'em': EMDataset
}

dsList = list(dsDict.keys())
scList = '16k 32k 64k 128k'.split()

dsSelected = st.selectbox('ds', dsList)
scSelected = st.selectbox('sc', scList)

if dsSelected != 'em':
    ds = dsDict[dsSelected](scSelected)
else:
    ds = dsDict[dsSelected]()

sz = len(ds)
dsIdxs = list(range(sz))
idxSelected = st.selectbox('idx', dsIdxs)
question, answer = ds[int(idxSelected)]
st.write(question)
st.write(answer)
