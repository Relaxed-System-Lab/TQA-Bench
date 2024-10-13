from benchmarkLoader.tableQALoader import TableQADataset
from benchmarkLoader.tableFVLoader import TableFVDataset
from benchmarkLoader.retrievalLoader import RetrievalDataset
from benchmarkLoader.cpaLoader import CPADataset
from benchmarkLoader.ctaLoader import CTADataset
from benchmarkLoader.emLoader import EMDataset

if __name__ == '__main__':
    qads = TableQADataset('16k', True)
    fvds = TableFVDataset('16k', True)
    retds = RetrievalDataset('16k', True)
    cpads = CPADataset('16k', True)
    ctads = CTADataset('16k', True)
    emds = EMDataset()

    for question, rightChoice in qads:
        print(question)
        print(rightChoice)
        break

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
    # for question, rightChoice in emds:
    #     print(question)
    #     print(rightChoice)
    #     break
