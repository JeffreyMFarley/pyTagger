import unittest
import os
import sys
import shutil
import random
import uuid
import binascii
import itertools
import pyTagger
from tests import *
from contextlib import contextmanager

CHECKIN_DIRECTORY = os.path.join(SOURCE_DIRECTORY, 'Checkin')
CHECKED_DIRECTORY = os.path.join(RESULT_DIRECTORY, 'checked_in')

# -----------------------------------------------------------------------------
# Module-Wide Routines
# -----------------------------------------------------------------------------

def walk(path):
    for currentDir, subdirs, files in os.walk(unicode(path)):
        # Get the absolute path of the currentDir parameter
        currentDir = os.path.abspath(currentDir)

        # Traverse through all files
        for fileName in files:
            fullPath = os.path.join(currentDir, fileName)
            yield fullPath

def resetFile(fileName):
    fromFile = os.path.join(CHECKIN_DIRECTORY, fileName)
    shutil.copy(fromFile, CHECKED_DIRECTORY)
    return os.path.join(CHECKED_DIRECTORY, fileName)

def setUpModule():
    if not os.path.exists(CHECKED_DIRECTORY):
        os.makedirs(CHECKED_DIRECTORY)

    for fullPath in walk(unicode(CHECKIN_DIRECTORY)):
        if fullPath[-3:].lower() in ['mp3']:
            shutil.copy(fullPath, CHECKED_DIRECTORY)

def tearDownModule():
    #shutil.rmtree(unicode(CHECKED_DIRECTORY))
    pass

# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------

class TestPrepareCheckIn(unittest.TestCase):

    @unittest.skipIf(sys.version >= '3', 'This test must be run in Python 2.x')
    def setUp(self):
        self.target = pyTagger.PrepareCheckIn()
        self.snapshot = self.target.reader

    def test_zee_last(self):
        self.target.run(CHECKED_DIRECTORY)

        columns = pyTagger.mp3_snapshot.Formatter.columns
        outFile = os.path.join(CHECKED_DIRECTORY, 'snapshot.json')

        self.snapshot.createFromScan(CHECKED_DIRECTORY, outFile, columns)
        result = self.snapshot.load(outFile)
        for k, v in result.items():
            self.assertEqual('DIG', v['media'])
            self.assertIsNotNone(v['ufid'])
            self.assertEqual([], v['comments'])
            self.assertIsNone(v['group'])
            self.assertIsNotNone(v['subtitle'])

    def test_stripBracket(self):
        fullPath = resetFile('01-01- Dreams [Explicit].mp3')
        self.target._process(fullPath)

        formatter = self.target.readerFormatter
        tags = self.snapshot.extractTags(fullPath, formatter)

        self.assertNotIn('[Explicit]', tags['title'])
        self.assertNotIn('[Explicit]', tags['album'])

if __name__ == '__main__':
    unittest.main()
