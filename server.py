import streamlit as st

from benchmarkUtils.stUtil import renderSelect, renderDataset

srcPath = 'dataset/scaledDB'

selectedSC, selectedDB = renderSelect(srcPath)
renderDataset(srcPath, selectedSC, selectedDB)
