from __future__ import unicode_literals
import io
import os
from collections import Counter
from pyTagger.operations.hash import hashFile
from pyTagger.operations.on_mp3 import extractImages as singleExtract
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


def buildHashTable(scanPath):
    table = {}
    for fullPath in walk(scanPath, True):
        v = hashFile(fullPath)
        table[v] = fullPath
    return table


def extractImages(scanPath, outputDir, id3Proxy):
    hashTable = {}
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    else:
        hashTable = buildHashTable(outputDir)

    c = Counter()
    for fullPath in walk(scanPath):
        c += singleExtract(id3Proxy, hashTable, outputDir, fullPath)
    return c


def extractImagesFrom(fileList, outputDir, id3Proxy):
    if not os.path.exists(fileList):
        raise ValueError(fileList + ' does not exist.')

    hashTable = {}
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    else:
        hashTable = buildHashTable(outputDir)

    c = Counter()
    with io.open(fileList, 'r', encoding='utf-8') as f:
        for l in f:
            fullPath = l.strip()

            # Check if the file has an extension of typical music files
            if fullPath[-3:].lower() in ['mp3']:
                c += singleExtract(id3Proxy, hashTable, outputDir, fullPath)
    return c
