import os
import json
import sys

if sys.version < '3':  # pragma: no cover
    import codecs
    _input = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
    _unicode = unicode
else:  # pragma: no cover
    _input = lambda fileName: open(fileName, 'r', encoding='utf-8')
    _unicode = lambda x: x


def toAbsolute(path):
    # where is _this_ script?
    thisScriptDir = os.path.dirname(__file__)

    # get the expected paths
    return os.path.join(thisScriptDir, path)


def loadJson(fileName):
    with _input(fileName) as f:
        return json.load(f)


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
