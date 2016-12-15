from __future__ import unicode_literals
import io
import os
import shutil
from collections import Counter
from pyTagger.operations.conform import LibraryStandard
from pyTagger.operations.hash import hashFile
from pyTagger.operations.name import buildPath
from pyTagger.operations.on_mp3 import extractImages as singleExtract
from pyTagger.utils import walk, saveJsonIncrementalDict
from pyTagger.utils import needsMove


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


def prepareForLibrary(path):
    i = 0
    standards = LibraryStandard()
    for fullPath in walk(path):
        standards.processFile(fullPath)
        i += 1
    return i


def renameFiles(sourceDir, destDir, reader):
    c = Counter()
    for fullPath in walk(sourceDir):
        try:
            tags = reader.extractTags(fullPath)
            jointed = buildPath(tags, fullPath[-3:])
            proposed = os.path.join(destDir, *jointed)

            if needsMove(fullPath, proposed):
                newPath = os.path.join(destDir, jointed[0], jointed[1], '')
                if not os.path.exists(newPath):
                    os.makedirs(newPath)
                shutil.move(fullPath, proposed)
                c['moved'] += 1
            else:
                c['skipped'] += 1

        except OSError:
            c['errors'] += 1
        except ValueError:
            c['collisions'] += 1

    return c
