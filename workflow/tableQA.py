import sys
sys.path.append('.')

from benchmarkUtils.database import DB
from benchmarkUtils.jsTool import JS
from benchmarkUtils.LLM import gptCall


prompts = JS('workflow/templates.json').loadJS()

def tableQAGeneration(dbPath, markdown=True):
    db = DB(dbPath)
    prompt = prompts['qa_workflow'].format(
        datasetInfo=db.defaultSerialization(markdown=markdown)
    )
    res = gptCall(
        'gpt-4o-mini',
        prompt,
        'tableQA',
        'dataset/log/tmp'
    )
    print(res)


if __name__ == '__main__':
    tableQAGeneration()
