import os
import streamlit as st
import sqlite3

import sys
sys.path.append('.')
from benchmarkUtils.database import DB
from benchmarkUtils.frontend import check_password

if not check_password():
    st.stop()

dbRoot = 'symDataset/scaledDB'
taskPath = 'symDataset/tasks/TableQA/dataset.sqlite'

scale = '8k 16k 32k 64k 128k'.split()

class datasetShow:
    def __init__(self, dbRoot, taskPath):
        self.dbRoot = dbRoot
        self.taskPath = taskPath
        self.conn = sqlite3.connect(self.taskPath)
        self.cur = self.conn.cursor()

    def listAllTables(self):
        self.cur.execute('SELECT name FROM sqlite_master  WHERE type=\'table\';')
        tableNames = []
        lst = self.cur.fetchall()
        if lst:
            for item in lst:
                tableNames.append(item[0])
        return tableNames

    def fetchItem(self, dbn, sc, dbIdx, sampleIdx, questionIdx):
        self.cur.execute('SELECT * FROM {dbn} WHERE scale=? AND dbIdx=? AND sampleIdx=? AND questionIdx=?;'.format(dbn=dbn),
                         (sc, dbIdx, sampleIdx, questionIdx))
        item = self.cur.fetchone()
        if item:
            return item
        return None

dtst = datasetShow(dbRoot, taskPath)
dbNames = dtst.listAllTables()
dbn = st.selectbox('Select a dataset', dbNames)
sc = st.selectbox('Select a scale', scale)
dbIdx = st.selectbox('Select dbIdx', list(range(10)))
sampleIdx = st.selectbox('Select sampleIdx', list(range(10)))
questionIdx = st.selectbox('Select questionIdx', list(range(14)))

item = dtst.fetchItem(dbn, sc, dbIdx, sampleIdx, questionIdx)

if item is not None:
    st.markdown(item[-6])
    for i in range(4):
        if i == item[-5]:
            st.markdown(f':red[{item[-4:][i]}]')
        else:
            st.markdown(item[-4:][i])

    dbp = os.path.join(dbRoot, sc, dbn, f'{dbIdx}.sqlite')
    db = DB(dbp)
    for k, v in db.tables.items():
        st.header(k)
        st.write(v)
    st.write(f'```sql\n{db.schema()}\n```')
