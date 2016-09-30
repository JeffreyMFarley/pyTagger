import sys
import os

if sys.platform.startswith('win'):
    RESULT_DIRECTORY = u'C:\\dvp\\MP3Tools\\TestOutput'
    SOURCE_DIRECTORY = u'C:\\dvp\\MP3Tools\\SampleData'
elif sys.platform.startswith('darwin'):
    RESULT_DIRECTORY = '/Users/farleyj/homebrew/var/test_output'
    SOURCE_DIRECTORY = '/Users/farleyj/Music/SampleData'
else:
    RESULT_DIRECTORY = '/var/test_output'
    SOURCE_DIRECTORY = '/SampleData'

if not os.path.exists(RESULT_DIRECTORY):
    os.makedirs(RESULT_DIRECTORY)

sampleFilesExist = os.path.exists(SOURCE_DIRECTORY)
