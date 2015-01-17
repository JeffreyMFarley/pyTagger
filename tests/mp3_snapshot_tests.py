import unittest
import os
import sys
import pyTagger

class TestMp3Snapshot(unittest.TestCase):

    def setUp(self):
        self.sourceDirectory = r'..\SampleData'
        self.resultDirectory = r'..\TestOutput'
        if not os.path.exists(self.resultDirectory):
            os.makedirs(self.resultDirectory)

    def tearDown(self):
        pass

    def test_allFieldsGrouped(self):
        target = pyTagger.mp3_snapshot.Formatter()
        columns = target.orderedAllColumns()

        # for testing that all fields are grouped
        missing = set(target.columns) - set(columns)
        assert not missing

    def test_01_scan(self):
        assert sys.version < '3', 'This test must be run in Python 2.x'

        target = pyTagger.Mp3Snapshot(False)
        columns = pyTagger.mp3_snapshot.Formatter.columns
        outFile = os.path.join(self.resultDirectory, r'snapshot.json')

        target.createFromScan(self.sourceDirectory, outFile, columns)
        assert os.path.getsize(outFile) > 0

    def test_02_convert(self):
        target = pyTagger.SnapshotConverter()
        inFile = os.path.join(self.resultDirectory, r'snapshot.json')
        outFile = os.path.join(self.resultDirectory, r'snapshot.txt')

        target.convert(inFile, outFile)
        assert os.path.getsize(outFile) > 0

if __name__ == '__main__':

    unittest.main(failfast=True, exit=False)