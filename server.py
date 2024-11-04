import streamlit as st

from benchmarkUtils.stUtil import renderSelect, renderDataset

srcPath = 'dataset/optmizedScaledDB'

selectedSC, selectedDB = renderSelect(srcPath)
renderDataset(srcPath, selectedSC, selectedDB)
