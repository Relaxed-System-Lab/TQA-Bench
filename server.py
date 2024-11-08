import streamlit as st

from benchmarkUtils.stUtil import renderSelect, renderDataset

srcPath = 'symDataset/scaledDB'

selectedSC, selectedDB = renderSelect(srcPath)
renderDataset(srcPath, selectedSC, selectedDB)
