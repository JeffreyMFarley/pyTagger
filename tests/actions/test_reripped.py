from __future__ import unicode_literals
import unittest
import pyTagger.actions.reripped as target
from pyTagger.utils import configurationOptions
try:
    from unittest.mock import patch, Mock, MagicMock
except ImportError:
    from mock import patch, Mock, MagicMock


class TestRerippedAction(unittest.TestCase):
    def setUp(self):
        import sys
        self.snapshot = {'foo': 'bar'}
        with patch.object(sys, 'argv', ['test', '1']):
            self.options = configurationOptions('reripped')

        p = patch('pyTagger.actions.reripped.Client')
        self.addCleanup(p.stop)
        self.client = p.start()
        self.client.return_value.exists.return_value = True

        p = patch('pyTagger.actions.reripped.os.path.exists')
        self.addCleanup(p.stop)
        self.path_exists = p.start()
        self.path_exists.return_value = True

        p = patch('pyTagger.actions.reripped.loadJson')
        self.addCleanup(p.stop)
        self.loadJson = p.start()
        self.loadJson.side_effect = AssertionError

    @patch('pyTagger.actions.reripped.uploadToElasticsearch')
    def test_buildIndex(self, uploader):
        target._buildIndex(self.options)
        uploader.assert_called_once_with(self.options)

    @patch('pyTagger.actions.reripped.findIsonoms')
    @patch('pyTagger.actions.reripped.saveJsonIncrementalArray')
    def test_findIsonoms(self, saveJson, findIsonoms):
        from pyTagger.models import TrackMatch

        def noop_coroutine(file):
            for i in [0, 1, 2, 3, 4, 5]:
                x = yield i
                self.assertEqual(x['status'], 'ready')

        self.loadJson.side_effect = [self.snapshot]
        saveJson.side_effect = noop_coroutine
        findIsonoms.return_value = [
            TrackMatch('ready', 'foo', 'bar', 11.0, None, None),
            TrackMatch('ready', 'foo', 'baz', 7.0, None, None),
            TrackMatch('ready', 'foo', 'qaz', 3.0, None, None)
        ]

        actual = target._findIsonoms(self.options, self.client)
        self.assertEqual(actual, '1 track(s) produced 3 rows')
        self.assertEqual(self.loadJson.call_count, 1)

    @patch('pyTagger.actions.reripped._buildIndex')
    def test_process_step1_index_not_exist(self, _buildIndex):
        self.client.return_value.exists.return_value = False
        with self.assertRaises(AssertionError):
            target.process(self.options)
        target._buildIndex.assert_called_once_with(self.options)

    @patch('pyTagger.actions.reripped._findIsonoms')
    def test_process_step1_isonoms_not_exist(self, findIsonoms):
        self.path_exists.return_value = False
        findIsonoms.return_value = 'foo'

        with self.assertRaises(AssertionError):
            target.process(self.options)

        target._findIsonoms.assert_called_once_with(self.options,
                                                    self.client.return_value)

    def test_process_step1_all_exist(self):
        with self.assertRaises(AssertionError):
            target.process(self.options)

    def test_process_step2(self):
        self.options.step = 2
        actual = target.process(self.options)
        self.assertEqual(actual, "Not Implemented")

if __name__ == '__main__':
    unittest.main()
