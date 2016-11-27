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
        with patch.object(sys, 'argv', ['test', '1']):
            self.options = configurationOptions('reripped')

        p = patch('pyTagger.actions.reripped.os.path.exists')
        self.addCleanup(p.stop)
        self.path_exists = p.start()
        self.path_exists.return_value = False

    @patch('pyTagger.actions.reripped.generateUfid')
    @patch('pyTagger.actions.reripped.union')
    @patch('pyTagger.actions.reripped.loadJson')
    def test_mergeAll(self, loadJson, union, generateUfid):
        ufid = 'NysA4aZ3TD+BykePnapEMw=='

        loadJson.return_value = [
            {'newTags': 'foo', 'oldTags': 'bar', 'newPath': '/foo/bar',
             'status': 'manual'},
            {'newTags': 'foo', 'oldTags': 'bar', 'newPath': '/foo/bar',
             'status': 'ready'},
            {'newTags': 'foo', 'oldTags': 'bar', 'newPath': '/foo/bar',
             'status': 'manual'}
        ]
        generateUfid.return_value = ufid
        union.return_value = {}
        expected = {
            '/foo/bar': {'id': ufid, 'ufid': {'DJTagger': ufid}}
        }

        actual = target._mergeAll(self.options)

        self.assertEqual(loadJson.call_count, 1)
        self.assertEqual(union.call_count, 3)
        self.assertEqual(union.call_args[0], ('foo', 'bar'))
        self.assertEqual(generateUfid.call_count, 2)
        self.assertEqual(actual, expected)

    @patch('pyTagger.actions.reripped.writeCsv')
    @patch('pyTagger.actions.reripped.isonom')
    def test_process_step1_isonom_ok(self, isonom, writeCsv):
        isonom.process.return_value = "Success"
        with patch.object(target, '_mergeAll', Mock()):
            actual = target._step1(self.options)

        self.assertEqual(actual, "Success")
        self.assertEqual(isonom.process.call_count, 1)
        self.assertEqual(writeCsv.call_count, 1)

    @patch('pyTagger.actions.reripped.isonom')
    def test_process_step1_isonom_fails(self, isonom):
        isonom.process.return_value = 'Foo'
        actual = target._step1(self.options)
        self.assertEqual(actual, 'Foo')

    @patch('pyTagger.actions.reripped.writeCsv')
    @patch('pyTagger.actions.reripped.isonom')
    def test_process_step1_goalsCsv_exists(self, isonom, writeCsv):
        self.path_exists.return_value = True
        actual = target.process(self.options)

        self.assertEqual(actual, "Success")
        self.assertEqual(isonom.process.call_count, 0)
        self.assertEqual(writeCsv.call_count, 0)

    def test_process_step2(self):
        self.options.step = 2
        actual = target.process(self.options)
        self.assertEqual(actual, "Not Implemented")

if __name__ == '__main__':
    unittest.main()
