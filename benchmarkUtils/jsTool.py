import os
import simplejson as json # simplejson主要是更兼容一点

class JS:
    def __init__(self, jsPath):
        self.jsPath = jsPath

    def newJS(self, content):
        with open(self.jsPath, 'w') as js:
            json.dump(content, js, indent=2, ignore_nan=True)
        return content

    def loadJS(self):
        if not os.path.isfile(self.jsPath):
            return []
        with open(self.jsPath, 'r') as js:
            content = json.load(js)
        return content

    def addJS(self, item):
        saveList = self.loadJS() + [item]
        self.newJS(saveList)
        return saveList

    def delJS(self, idx):
        saveList = self.loadJS()
        del saveList[idx]
        self.newJS(saveList)
        return saveList

    def condAdd(self, item, conds):
        """
        条件添加, 在conds这一key中都不重复则视为可以添加
        """
        lst = self.loadJS()
        for c in conds:
            if item[c] in [it[c] for it in lst]:
                return False
        lst.append(item)
        self.newJS(lst)
        return True
