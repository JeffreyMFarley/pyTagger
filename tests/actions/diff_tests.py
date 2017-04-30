from __future__ import unicode_literals
import unittest
import pyTagger.actions.diff as target
from pyTagger.utils import configurationOptions
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

fixture_a = {
    'foo': {'album': None, 'artist': 'w', 'bitRate': 128, 'id': '123456'},
    'bar': {'album': 1, 'artist': None, 'length': 438, 'id': '987654'}
}
fixture_b = {
    'foo': {'album': 1, 'artist': 'www', 'id': '123456'},
    'bar': {'album': 1, 'artist': 'w', 'id': '987654'}
}


class TestDiffAction(unittest.TestCase):
    def setUp(self):
        import sys
        with patch.object(sys, 'argv', ['test', 'a.json', 'b.json', 'c.json']):
            self.options = configurationOptions('diff')

    def noop_coroutine(self, outfile, compact):
        self.assertEqual(outfile, 'c.json')
        self.assertEqual(compact, False)
        for i in [0, 1, 2, 3, 4]:
            k, v = yield i

    @patch('pyTagger.actions.diff.saveJsonIncrementalDict')
    @patch('pyTagger.actions.diff.loadJson')
    def test_process(self, loadJson, saveJson):
        loadJson.side_effect = [dict(fixture_a), dict(fixture_b)]
        saveJson.side_effect = self.noop_coroutine
        actual = target.process(self.options)
        self.assertEqual(actual, '1 tags processed')

    @patch('pyTagger.actions.diff.saveJsonIncrementalDict')
    @patch('pyTagger.actions.diff.loadJson')
    def test_process_include_nulls(self, loadJson, saveJson):
        self.options.include_nulls = True
        loadJson.side_effect = [dict(fixture_a), dict(fixture_b)]
        saveJson.side_effect = self.noop_coroutine
        actual = target.process(self.options)
        self.assertEqual(actual, '2 tags processed')

    @patch('pyTagger.actions.diff.saveJsonIncrementalDict')
    @patch('pyTagger.actions.diff.loadJson')
    def test_process_match_on_ids(self, loadJson, saveJson):
        self.options.match_on = 'id'
        loadJson.side_effect = [dict(fixture_a), dict(fixture_b)]
        saveJson.side_effect = self.noop_coroutine
        actual = target.process(self.options)
        self.assertEqual(actual, '1 tags processed')

    @patch('pyTagger.actions.diff.saveJsonIncrementalDict')
    @patch('pyTagger.actions.diff.loadJson')
    def test_process_match_on_ids_missing_ids(self, loadJson, saveJson):
        self.options.match_on = 'id'
        a = dict(fixture_a)
        del a['foo']['id']
        b = dict(fixture_b)
        del b['foo']['id']

        loadJson.side_effect = [a, b]
        saveJson.side_effect = self.noop_coroutine
        actual = target.process(self.options)
        self.assertEqual(actual, '0 tags processed')

if __name__ == '__main__':
    unittest.main()
