from __future__ import unicode_literals
import unittest
import pyTagger.actions.reripped as target
from pyTagger.utils import configurationOptions
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


class TestRerippedAction(unittest.TestCase):
    def setUp(self):
        import sys
        self.snapshot = {'foo': 'bar'}
        with patch.object(sys, 'argv', ['test', '1']):
            self.options = configurationOptions('reripped')

    @patch('pyTagger.actions.reripped.uploadToElasticsearch')
    def test_step0(self, uploader):
        target._step0(self.options)
        uploader.assert_called_once_with(self.options)

    @patch('pyTagger.actions.reripped.findIsonoms')
    @patch('pyTagger.actions.reripped.saveJsonIncrementalArray')
    @patch('pyTagger.actions.reripped.loadJson')
    @patch('pyTagger.actions.reripped.Client')
    def test_step1(self, client, loadJson, saveJson, findIsonoms):
        from collections import namedtuple

        Isonom = namedtuple('Isonom', ['status', 'oldPath', 'newPath'])

        loadJson.return_value = self.snapshot
        saveJson.return_value = Mock(['next', 'send', 'close'])
        saveJson.return_value.send.side_effect = [1, 2, 3]
        findIsonoms.return_value = [
            Isonom('ready', 'foo', 'bar'),
            Isonom('ready', 'foo', 'baz'),
            Isonom('ready', 'foo', 'qaz')
        ]

        actual = target._step1(self.options, client)
        self.assertEqual(actual, 'Step 1: 1 track(s) produced 3 rows')
        self.assertEqual(loadJson.call_count, 1)
        self.assertEqual(saveJson.return_value.next.call_count, 1)
        self.assertEqual(saveJson.return_value.send.call_count, 3)
        self.assertEqual(saveJson.return_value.close.call_count, 1)

    @patch('pyTagger.actions.reripped._step1')
    @patch('pyTagger.actions.reripped._step0')
    @patch('pyTagger.actions.reripped.Client')
    def test_process_step1_index_not_exist(self, client, step0, step1):
        client.return_value.exists.return_value = False
        step0.return_value = None
        step1.return_value = 'foo'

        actual = target.process(self.options)

        self.assertEqual(actual, 'foo')
        target._step0.assert_called_once_with(self.options)
        target._step1.assert_called_once_with(self.options,
                                              client.return_value)

    @patch('pyTagger.actions.reripped._step1')
    @patch('pyTagger.actions.reripped._step0')
    @patch('pyTagger.actions.reripped.Client')
    def test_process_step1_index_exist(self, client, step0, step1):
        client.return_value.exists.return_value = True
        step0.return_value = None
        step1.return_value = 'foo'

        actual = target.process(self.options)

        self.assertEqual(actual, 'foo')
        self.assertEqual(target._step0.call_count, 0)
        target._step1.assert_called_once_with(self.options,
                                              client.return_value)

    def test_process_step2(self):
        self.options.step = 2
        actual = target.process(self.options)
        self.assertEqual(actual, "Not Implemented")

if __name__ == '__main__':
    unittest.main()
