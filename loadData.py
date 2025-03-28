from benchmarkLoader.tableQALoader import TableQADataset
from benchmarkLoader.tableFVLoader import TableFVDataset
from benchmarkLoader.retrievalLoader import RetrievalDataset
from benchmarkLoader.cpaLoader import CPADataset
from benchmarkLoader.ctaLoader import CTADataset
from benchmarkLoader.emLoader import EMDataset

import re
def extractAnswer(text:str)->str:
    patt = r'answer:\s*([A-F]+)'
    grps = re.findall(patt, text, re.IGNORECASE)
    if grps:
        return grps[-1].upper()
    return ''

if __name__ == '__main__':
    qads = TableQADataset('16k', True)
    fvds = TableFVDataset('16k', True)
    retds = RetrievalDataset('16k', True)
    cpads = CPADataset('16k', True)
    ctads = CTADataset('16k', True)
    emds = EMDataset()

    # print('qads', len(qads))
    # print('fvds', len(fvds))
    # print('retds', len(retds))
    # print('cpads', len(cpads))
    # print('ctads', len(ctads))
    # print('emds', len(emds))

    # for question, rightChoice in qads:
    #     print(question)
    #     print(rightChoice)
    #     break
    #
    # for question, rightChoice in fvds:
    #     print(question)
    #     print(rightChoice)
    #     break
    #
    # for question, rightChoice in retds:
    #     print(question)
    #     print(rightChoice)
    #     break
    #
    # for question, rightChoice in cpads:
    #     print(question)
    #     print(rightChoice)
    #     break
    #
    # for question, rightChoice in ctads:
    #     print(question)
    #     print(rightChoice)
    #     break
    #
    for question, rightChoice in emds:
        print(question)
        print(rightChoice)
        break
