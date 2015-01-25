import unittest
import os
import sys
import pyTagger
from tests import *

class TestIntegration(unittest.TestCase):

    @unittest.skipIf(sys.version > '3', 'This test must be run in Python 2.x')
    def test_01_scan(self):
        target = pyTagger.Mp3Snapshot(False)
        columns = pyTagger.mp3_snapshot.Formatter.columns
        outFile = os.path.join(RESULT_DIRECTORY, r'snapshot.json')

        target.createFromScan(SOURCE_DIRECTORY, outFile, columns)
        assert os.path.getsize(outFile) > 0

    def test_02_convert(self):
        target = pyTagger.SnapshotConverter()
        inFile = os.path.join(RESULT_DIRECTORY, r'snapshot.json')
        outFile = os.path.join(RESULT_DIRECTORY, r'snapshot.txt')

        target.convert(inFile, outFile)
        assert os.path.getsize(outFile) > 0

if __name__ == '__main__':

    unittest.main(failfast=True, exit=False)