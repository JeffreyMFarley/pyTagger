import datetime
import unittest
import pyTagger.actions.scan as target
from collections import namedtuple
from pyTagger.utils import configurationOptions
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

MockStats = namedtuple('_stat', ['st_mtime'])


class TestScanAction(unittest.TestCase):
    def setUp(self):
        self.options = configurationOptions('scan')

        class fakedatetime(datetime.datetime):
            @classmethod
            def fromtimestamp(cls, timestamp):
                return datetime.datetime(2010, 5, 25)

        patcher = patch('datetime.datetime', fakedatetime)
        self.addCleanup(patcher.stop)
        patcher.start()

    def test_postelDate_fullIso(self):
        actual = target.postelDate('2013-02-03T17:27:00')
        self.assertEqual(actual.year, 2013)
        self.assertEqual(actual.month, 2)
        self.assertEqual(actual.day, 3)
        self.assertEqual(actual.hour, 17)
        self.assertEqual(actual.minute, 27)

    def test_postelDate_partial(self):
        actual = target.postelDate('2013-02')
        self.assertEqual(actual.year, 2013)
        self.assertEqual(actual.month, 2)
        self.assertEqual(actual.day, 1)
        self.assertEqual(actual.hour, 0)
        self.assertEqual(actual.minute, 0)

    def test_buildFilter_notMp3(self):
        filterFn = target.buildFilter(self.options)
        actual = filterFn('foo.txt')
        self.assertEqual(actual, False)

    @patch('pyTagger.actions.scan.creationDate')
    @patch('os.stat')
    def test_buildFilter_noDates(self, stat, creationDate):
        stat.return_value = MockStats(1)
        creationDate.return_value = 2
        filterFn = target.buildFilter(self.options)
        actual = filterFn('foo.mp3')
        self.assertEqual(actual, True)

    @patch('pyTagger.actions.scan.creationDate')
    @patch('os.stat')
    def test_buildFilter_withDates(self, stat, creationDate):
        self.options.modified_min = '2011'
        stat.return_value = MockStats(1)
        creationDate.return_value = 2
        filterFn = target.buildFilter(self.options)
        actual = filterFn('foo.mp3')
        self.assertEqual(actual, False)

    @patch('pyTagger.actions.scan.ID3Proxy')
    @patch('pyTagger.actions.scan.buildSnapshot')
    def test_process(self, buildSnapshot, id3Proxy):
        id3Proxy.return_value = 'id3Proxy goes here'
        buildSnapshot.return_value = (420, 99)

        actual = target.process(self.options)

        self.assertEqual(id3Proxy.call_count, 1)
        buildSnapshot.assert_called_once_with(self.options.path,
                                              self.options.outfile,
                                              'id3Proxy goes here',
                                              False, None)
        self.assertEqual(actual, 'Extracted tags from 420 files\nFailed 99')

    @patch('pyTagger.actions.scan.ID3Proxy')
    @patch('pyTagger.actions.scan.buildSnapshot')
    @patch('pyTagger.actions.scan.buildFilter')
    def test_process_with_date(self, buildFilter, buildSnapshot, id3Proxy):
        self.options.modified_min = '2011'
        buildFilter.return_value = 'filter!'
        buildSnapshot.return_value = (420, 99)
        id3Proxy.return_value = 'id3Proxy goes here'

        actual = target.process(self.options)

        self.assertEqual(id3Proxy.call_count, 1)
        buildSnapshot.assert_called_once_with(self.options.path,
                                              self.options.outfile,
                                              'id3Proxy goes here',
                                              False, 'filter!')
        self.assertEqual(actual, 'Extracted tags from 420 files\nFailed 99')

if __name__ == '__main__':
    unittest.main()
