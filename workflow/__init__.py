import os
import sys
sys.path.append('.')
from benchmarkUtils.jsTool import JS

promptPath = 'workflow/templates.json'

prompts = JS(promptPath).loadJS()

taskRoot = 'dataset/task'

scaleRoot = 'dataset/scaledDB/'
qaRoot = os.path.join(taskRoot, 'tableQA')
refScale = '16k'

scaledDict:dict={
    '128k': (64, 96),
    '64k': (32, 48),
    '32k': (16, 24),
    '16k': (8, 12),
    '8k': (4, 6)
}
