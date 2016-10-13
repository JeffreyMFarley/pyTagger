from __future__ import unicode_literals
import io
import os
import json
import sys
from configargparse import getArgumentParser
from itertools import count

if sys.version < '3':  # pragma: no cover
    import codecs
    _input = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
    _unicode = unicode
else:  # pragma: no cover
    _input = lambda fileName: open(fileName, 'r', encoding='utf-8')
    _unicode = lambda x: x

# -----------------------------------------------------------------------------

defaultConfigFiles = ['./config.ini', '~/pyTagger.ini']

rootParser = getArgumentParser(
    default_config_files=defaultConfigFiles,
    args_for_setting_config_path=['--config'],
    args_for_writing_out_config_file=['--save-config']
)


def configurationOptions(name):
    p = getArgumentParser(name)
    options, _ = p.parse_known_args()
    return options

# -----------------------------------------------------------------------------


def toAbsolute(path):
    # where is _this_ script?
    thisScriptDir = os.path.dirname(__file__)

    # get the expected paths
    return os.path.join(thisScriptDir, path)


def loadJson(fileName):
    with _input(fileName) as f:
        return json.load(f)


def saveJson(fileName, o):
    with io.open(fileName, 'w', encoding='utf-8') as f:
        f.write(_unicode(json.dumps(o, ensure_ascii=False)))


def saveJsonIncrementalArray(fileName):
    sep = '\n'
    with io.open(fileName, 'w', encoding='utf-8') as f:
        f.write('[')
        try:
            for i in count():  # pragma: no branch
                row = yield i
                f.write(sep)
                f.write(_unicode(json.dumps(row, ensure_ascii=False)))
                sep = ',\n'
        finally:
            f.write('\n]')


def walk(directory, showAll=False):
    for currentDir, _, files in os.walk(_unicode(directory)):
        # Get the absolute path of the currentDir parameter
        currentDir = os.path.abspath(currentDir)

        # Traverse through all files
        for fileName in files:
            fullPath = os.path.join(currentDir, fileName)

            # Check if the file has an extension of typical music files
            if showAll or fullPath[-3:].lower() in ['mp3']:
                yield fullPath
