import os
import json
from os.path import isfile

class JS:
    def __init__(self, jsPath):
        self.jsPath = jsPath

    def newJS(self, content):
        with open(self.jsPath, 'w') as js:
            json.dump(content, js)
        return content

    def loadJS(self):
        if not os.path.isfile(self.jsPath):
            return []
        with open(self.jsPath, 'r') as js:
            content = json.load(js)
        return content

    def addJS(self, item):
        saveList = [item]
        if os.path.isfile(self.jsPath):
            saveList = self.loadJS() + saveList
        return saveList
