from __future__ import unicode_literals
import io
import os
import shutil
from collections import Counter
from pyTagger.operations.conform import LibraryStandard
from pyTagger.operations.hash import hashFile
from pyTagger.operations.name import buildPath
from pyTagger.operations.on_mp3 import extractImages as singleExtract
from pyTagger.utils import saveJsonIncrementalDict

import sys
if sys.version < '3':  # pragma: no cover
    _unicode = unicode
else:  # pragma: no cover
    _unicode = lambda x: x

# -----------------------------------------------------------------------------
# Walk Variations


def _filterAll(fullPath):
    return fullPath != ''


def _filterMp3s(fullPath):
    return fullPath[-3:].lower() in ['mp3']


def _walkDirectory(path, filterFn):
    for currentDir, _, files in os.walk(_unicode(path)):
        # Get the absolute path of the currentDir parameter
        currentDir = os.path.abspath(currentDir)

        # Traverse through all files
        for fileName in files:
            fullPath = os.path.join(currentDir, fileName)

            if filterFn(fullPath):
                yield fullPath


def _walkFile(path, filterFn):
    with io.open(path, 'r', encoding='utf-8') as f:
        for l in f:
            fullPath = os.path.abspath(l.strip())

            if filterFn(fullPath):
                yield fullPath


def walk(path):
    if os.path.isfile(path):
        for f in _walkFile(path, _filterMp3s):
            yield f
    elif os.path.isdir(path):
        for f in _walkDirectory(path, _filterMp3s):
            yield f
    else:
        raise ValueError(path + ' is not a file or directory')


def walkAll(path):
    if os.path.isfile(path):
        for f in _walkFile(path, _filterAll):
            yield f
    elif os.path.isdir(path):
        for f in _walkDirectory(path, _filterAll):
            yield f
    else:
        raise ValueError(path + ' is not a file or directory')

# -----------------------------------------------------------------------------
# Local Helper Functions


def needsMove(current, proposed):
    if current == proposed:
        return False

    if os.path.exists(proposed):
        raise ValueError(proposed + ' already exists. Avoiding collision')

    return True

# -----------------------------------------------------------------------------
# Directory Functions


def buildSnapshot(path, outFileName, id3Reader, compact=False):
    output = saveJsonIncrementalDict(outFileName, compact)

    extracted = next(output)
    failed = 0

    for fullPath in walk(path):
        row = id3Reader.extractTags(fullPath)
        if row:
            pair = (fullPath.replace('\\', '\\\\'), row)
            extracted = output.send(pair)
        else:
            failed += 1

    output.close()

    return extracted, failed


def buildHashTable(path):
    table = {}
    for fullPath in walkAll(path):
        v = hashFile(fullPath)
        table[v] = fullPath
    return table


def deleteEmptyDirectories(path):
    # Flatten the list of directories, walking bottom up
    queue = []
    for currentDir, _, _ in os.walk(_unicode(path), topdown=False):
        queue.append(currentDir)

    # Now check the values, `os.walk` does not recognize intermediate deletes
    success, skipped = 0, 0
    for p in queue:
        size = len(os.listdir(p))
        if not size:
            os.rmdir(p)
            success += 1
        else:
            skipped += 1

    return success, skipped


def deleteFiles(path):
    success, failed = 0, 0
    for fileName in walkAll(path):
        try:
            os.remove(fileName)
            success += 1
        except OSError:
            failed += 1

    return success, failed


def extractImages(path, outputDir, id3Proxy):
    hashTable = {}
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    else:
        hashTable = buildHashTable(outputDir)

    c = Counter()
    for fullPath in walk(path):
        c += singleExtract(id3Proxy, hashTable, outputDir, fullPath)
    return c


def prepareForLibrary(path):
    i = 0
    standards = LibraryStandard()
    for fullPath in walk(path):
        standards.processFile(fullPath)
        i += 1
    return i


def renameFiles(path, destDir, reader):
    c = Counter()
    for fullPath in walk(path):
        try:
            tags = reader.extractTags(fullPath)
            if not tags:
                raise OSError
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


def replaceFiles(fileOfFilePairs):
    c = Counter()
    with io.open(fileOfFilePairs, 'r', encoding='utf-8') as f:
        for l in f:
            source, dest = l.strip().split('\t')
            if not os.path.exists(source):
                c['missing-source'] += 1
            elif not os.path.exists(dest):
                c['missing-dest'] += 1
            else:
                try:
                    shutil.move(source, dest)
                    c['replaced'] += 1
                except Exception:
                    c['errors'] += 1
    return c
