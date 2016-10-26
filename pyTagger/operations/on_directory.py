from __future__ import unicode_literals
from pyTagger.utils import walk, saveJsonIncrementalDict


def buildSnapshot(scanPath, outFileName, id3Reader, compact=False):
    output = saveJsonIncrementalDict(outFileName, compact)

    extracted = next(output)
    failed = 0

    for fullPath in walk(scanPath):
        row = id3Reader.extractTags(fullPath)
        if row:
            pair = (fullPath.replace('\\', '\\\\'), row)
            extracted = output.send(pair)
        else:
            failed += 1

    output.close()

    return extracted, failed
