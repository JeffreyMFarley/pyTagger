import sys
import os

if sys.platform.startswith('win'):
    RESULT_DIRECTORY = r'C:\dvp\MP3Tools\TestOutput'
    SOURCE_DIRECTORY = r'C:\dvp\MP3Tools\SampleData'
else:
    RESULT_DIRECTORY = '../TestOutput'
    SOURCE_DIRECTORY = '../SampleData'

if not os.path.exists(RESULT_DIRECTORY):
    os.makedirs(RESULT_DIRECTORY)

