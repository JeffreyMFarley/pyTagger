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
from pyTagger.models import Snapshot
from pyTagger.utils import loadJson, walk
if sys.version >= '3':
    unicode = lambda x: x

CHECKIN_DIRECTORY = os.path.join(SOURCE_DIRECTORY, 'Checkin')
CHECKED_DIRECTORY = os.path.join(RESULT_DIRECTORY, 'checked_in')

# -----------------------------------------------------------------------------
# Module-Wide Routines
# -----------------------------------------------------------------------------


def resetFile(fileName):
    fromFile = os.path.join(CHECKIN_DIRECTORY, fileName)
    shutil.copy(fromFile, CHECKED_DIRECTORY)
    return os.path.join(CHECKED_DIRECTORY, fileName)


def setUpModule():
    if sampleFilesExist and not os.path.exists(CHECKED_DIRECTORY):
        os.makedirs(CHECKED_DIRECTORY)

    for fullPath in walk(CHECKIN_DIRECTORY, True):
        shutil.copy(fullPath, CHECKED_DIRECTORY)


def tearDownModule():
    #shutil.rmtree(CHECKED_DIRECTORY)
    pass

# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------


class TestPrepareCheckIn(unittest.TestCase):

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def setUp(self):
        self.target = pyTagger.PrepareCheckIn()
        self.snapshot = self.target.reader

    def test_zee_last(self):
        self.target.run(CHECKED_DIRECTORY)

        columns = Snapshot.orderedAllColumns()
        outFile = os.path.join(CHECKED_DIRECTORY, 'snapshot.json')

        self.snapshot.createFromScan(CHECKED_DIRECTORY, outFile, columns)
        result = loadJson(outFile)
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
