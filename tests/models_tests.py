import unittest
from pyTagger.models import Snapshot
from pyTagger.utils import configurationOptions
from tests import *


class TestSnapshot(unittest.TestCase):
    def setUp(self):
        self.options = configurationOptions('snapshot')

    def test_columnsFromSnapshot_hasUnknown(self):
        data = {
            'somefile.mp3': {
                'title': 'foo',
                'zzz': 'bar',
                'aaa': 'baz'
            }
        }
        actual = Snapshot.columnsFromSnapshot(data)
        self.assertEqual(actual, ['title', 'aaa', 'zzz'])

    def test_columnsFromArgs_basic(self):
        self.options.basic = True
        actual = Snapshot.columnsFromArgs(self.options)
        self.assertEqual(actual, Snapshot.basic)

    def test_columnsFromArgs_songwriting(self):
        self.options.songwriting = True
        actual = Snapshot.columnsFromArgs(self.options)
        self.assertEqual(actual, Snapshot.songwriting)

    def test_columnsFromArgs_production(self):
        self.options.production = True
        actual = Snapshot.columnsFromArgs(self.options)
        self.assertEqual(actual, Snapshot.production)

    def test_columnsFromArgs_distribution(self):
        self.options.distribution = True
        actual = Snapshot.columnsFromArgs(self.options)
        self.assertEqual(actual, Snapshot.distribution)

    def test_columnsFromArgs_library(self):
        self.options.library = True
        actual = Snapshot.columnsFromArgs(self.options)
        self.assertEqual(actual, Snapshot.library)

    def test_columnsFromArgs_mp3Info(self):
        self.options.mp3Info = True
        actual = Snapshot.columnsFromArgs(self.options)
        self.assertEqual(actual, Snapshot.mp3Info)

    def test_columnsFromArgs_all(self):
        self.options.all = True
        actual = Snapshot.columnsFromArgs(self.options)
        self.assertEqual(actual, Snapshot.orderedAllColumns())


if __name__ == '__main__':
    unittest.main()
