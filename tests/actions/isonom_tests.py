from __future__ import unicode_literals
import unittest
import pyTagger.actions.isonom as target
from pyTagger.utils import configurationOptions
try:
    from unittest.mock import patch, Mock, MagicMock
except ImportError:
    from mock import patch, Mock, MagicMock


class TestIsonomAction(unittest.TestCase):
    def setUp(self):
        import sys
        self.snapshot = {'foo': 'bar'}
        with patch.object(sys, 'argv', ['test']):
            self.options = configurationOptions('isonom')

        p = patch('pyTagger.actions.isonom.Client')
        self.addCleanup(p.stop)
        self.client = p.start()
        self.client.return_value.exists.return_value = True

        p = patch('pyTagger.actions.isonom.os.path.exists')
        self.addCleanup(p.stop)
        self.path_exists = p.start()
        self.path_exists.return_value = True

        p = patch('pyTagger.actions.isonom.loadJson')
        self.addCleanup(p.stop)
        self.loadJson = p.start()
        self.loadJson.return_value = self.snapshot

        p = patch('pyTagger.actions.isonom.Interview')
        self.addCleanup(p.stop)
        self.interview = p.start()
        self.interview.return_value = Mock(spec=[
            'isComplete', 'conduct', 'saveState', 'userQuit'
        ])
        self.interview.return_value.isComplete.return_value = True
        self.interview.return_value.userQuit = False

    @patch('pyTagger.actions.isonom.uploadToElasticsearch')
    def test_buildIndex(self, uploader):
        target._buildIndex(self.options)
        uploader.assert_called_once_with(self.options)

    @patch('pyTagger.actions.isonom.findIsonoms')
    @patch('pyTagger.actions.isonom.saveJsonIncrementalArray')
    def test_findIsonoms(self, saveJson, findIsonoms):
        from pyTagger.models import TrackMatch

        def noop_coroutine(file):
            for i in [0, 1, 2, 3, 4, 5]:
                x = yield i
                self.assertEqual(x['status'], 'ready')

        saveJson.side_effect = noop_coroutine
        findIsonoms.return_value = [
            TrackMatch('ready', 'foo', 'bar', 11.0, None, None),
            TrackMatch('ready', 'foo', 'baz', 7.0, None, None),
            TrackMatch('ready', 'foo', 'qaz', 3.0, None, None)
        ]

        actual = target._findIsonoms(self.options, self.client)
        self.assertEqual(actual, '1 track(s) produced 3 rows')
        self.assertEqual(self.loadJson.call_count, 1)

    @patch('pyTagger.actions.isonom._buildIndex')
    def test_process_index_not_exist(self, _buildIndex):
        self.client.return_value.exists.return_value = False
        actual = target.process(self.options)
        self.assertEqual(actual, "Success")
        target._buildIndex.assert_called_once_with(self.options)

    @patch('pyTagger.actions.isonom._findIsonoms')
    def test_process_isonoms_not_exist(self, findIsonoms):
        self.path_exists.return_value = False
        findIsonoms.return_value = 'foo'

        actual = target.process(self.options)

        self.assertEqual(actual, "Success")
        target._findIsonoms.assert_called_once_with(self.options,
                                                    self.client.return_value)

    def test_process_discard_interview(self):
        self.interview.return_value.isComplete.return_value = False
        self.interview.return_value.conduct.return_value = False
        actual = target.process(self.options)
        self.assertFalse(self.interview.return_value.saveState.called)
        self.assertEqual(actual, "Interview Not Complete")

    def test_process_partial_interview(self):
        self.interview.return_value.isComplete.return_value = False
        self.interview.return_value.conduct.return_value = True
        self.interview.return_value.userQuit = True
        actual = target.process(self.options)
        self.assertTrue(self.interview.return_value.saveState.called)
        self.assertEqual(actual, "Interview Not Complete")

    def test_process_finished_interview(self):
        self.interview.return_value.isComplete.return_value = False
        self.interview.return_value.conduct.return_value = True
        actual = target.process(self.options)
        self.assertTrue(self.interview.return_value.saveState.called)
        self.assertEqual(actual, "Success")

    def test_process_all_exist(self):
        actual = target.process(self.options)
        self.assertEqual(actual, "Success")
        self.assertFalse(self.interview.return_value.conduct.called)
        self.assertFalse(self.interview.return_value.saveState.called)

if __name__ == '__main__':
    unittest.main()
