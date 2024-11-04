
import hmac
import json
import os
import streamlit as st

import sys
sys.path.append('.')
from benchmarkUtils.database import DB
from benchmarkUtils.jsTool import JS

def check_password():
    """Returns `True` if the user had a correct password."""
    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False

class FrontEndDataset(DB):
    """
    继承原始的DB, 添加渲染功能, 可以直接渲染数据库
    """
    def renderDataset(self):
        tables = self.initDataFrame()
        for k, v in tables.items():
            st.header(k)
            st.write(v)

def renderSelect(srcPath='dataset/scaledDB/'):
    scales = os.listdir(srcPath)
    selectedSC = st.selectbox('Select a scale', scales)
    selectedScaledPath = os.path.join(srcPath, str(selectedSC)) # 由于IDE容易将selectedSC视为无类型, 所以这里得做一个转化
    databases = os.listdir(selectedScaledPath)
    selectedDS = st.selectbox('Select a Database', databases)
    return selectedSC, selectedDS

def renderDataset(srcPath, selectedSC, selectedDS):
    # 渲染选中的数据集
    dsRoot = os.path.join(srcPath, selectedSC, selectedDS)
    dsPath = os.path.join(dsRoot, f'{selectedDS}.sqlite')
    jsPath = os.path.join(dsRoot, 'sampleInfo.json')
    sampInfo = JS(jsPath).loadJS()
    st.write(sampInfo)
    fed = FrontEndDataset(dsPath)
    st.write(len(fed.tables))
    fed.renderDataset()
    st.write(f'```sql\n{fed.schema()}\n```')

def renderItems(dstPath, selectedDs, keyRenMap):
    return None
    datasetPath = os.path.join(dstPath, f'{selectedDs}.json')
    if not os.path.isfile(datasetPath):
        # 倘若不存在该文件, 则渲染一个空数据集
        with open(datasetPath, 'w') as js:
            json.dump([], js)
    
    with open(datasetPath, 'r') as js:
        items = json.load(js)
    
    itemIdx = st.selectbox('Select', ['+'] + list(range(len(items))))

    saveItem = {}
    if itemIdx == '+':
        with st.form('Add', clear_on_submit=True):
            for k, r in keyRenMap.items():
                if r == st.text_area:
                    saveItem[k] = r(k, height=300)
                else:
                    saveItem[k] = r(k)
            # addBut = st.form_submit_button('Add', use_container_width=True)
            col1, col2 = st.columns(2)
            with col1:
                addBut = st.form_submit_button('Add', use_container_width=True)
            if addBut:
                items.append(saveItem)
                JS(datasetPath).newJS(items)
                st.rerun()
    else:
        idx = int(itemIdx)
        saveItem = items[idx]
        with st.form('Edit / Delete'):
            for k, r in keyRenMap.items():
                if r == st.text_area:
                    saveItem[k] = r(k, saveItem[k], height=300)
                else:
                    saveItem[k] = r(k, saveItem[k])
            # editBut = st.form_submit_button('Edit')
            # delBut = st.form_submit_button('Delete', type='primary')
            col1, col2 = st.columns(2)
            with col1:
                editBut = st.form_submit_button('Edit', use_container_width=True)
            with col2:
                delBut = st.form_submit_button('Delete', type='primary', use_container_width=True)
            if editBut:
                items[idx] = saveItem
                JS(datasetPath).newJS(items)
            if delBut:
                del items[idx]
                JS(datasetPath).newJS(items)
                st.rerun()
