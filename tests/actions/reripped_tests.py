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

    @patch('pyTagger.actions.reripped.saveJsonIncrementalDict')
    @patch('pyTagger.actions.reripped.generateUfid')
    @patch('pyTagger.actions.reripped.union')
    @patch('pyTagger.actions.reripped.loadJson')
    def test_mergeAll(self, loadJson, union, generateUfid, saveJson):
        ufid = 'NysA4aZ3TD+BykePnapEMw=='

        def noop_coroutine(file, compact):
            for i in [0, 1, 2, 3, 4]:
                k, v = yield i
                self.assertEqual(k, '/foo/bar')
                self.assertEqual(v['id'], ufid)
                self.assertEqual(v['ufid']['DJTagger'], ufid)

        loadJson.return_value = [
            {'newTags': 'foo', 'oldTags': 'bar', 'newPath': '/foo/bar'},
            {'newTags': 'foo', 'oldTags': 'bar', 'newPath': '/foo/bar'},
            {'newTags': 'foo', 'oldTags': 'bar', 'newPath': '/foo/bar'}
        ]
        generateUfid.return_value = ufid
        union.side_effect = [
            {},
            {'id': ufid, 'ufid': {'DJTagger': ufid}},
            {'id': ''}
        ]
        saveJson.side_effect = noop_coroutine

        actual = target._mergeAll(self.options)

        self.assertEqual(loadJson.call_count, 1)
        self.assertEqual(union.call_count, 3)
        self.assertEqual(union.call_args[0], ('foo', 'bar'))
        self.assertEqual(generateUfid.call_count, 2)
        self.assertEqual(saveJson.call_count, 1)
        self.assertEqual(actual, 3)

    @patch('pyTagger.actions.reripped.isonom')
    def test_process_step1_isonom_ok(self, isonom):
        isonom.process.return_value = "Success"
        with patch.object(target, '_mergeAll',
                          Mock(side_effect=AssertionError)):
            with self.assertRaises(AssertionError):
                target.process(self.options)

    @patch('pyTagger.actions.reripped.isonom')
    def test_process_step1_isonom_fails(self, isonom):
        isonom.process.return_value = 'Foo'
        actual = target.process(self.options)
        self.assertEqual(actual, 'Foo')

    @patch('pyTagger.actions.reripped.writeCsv')
    @patch('pyTagger.actions.reripped.loadJson')
    @patch('pyTagger.actions.reripped.isonom')
    def test_process_step1_goalsJson_exists(self, isonom, loadJson, writeCsv):
        self.path_exists.return_value = True
        with patch.object(target, '_mergeAll', Mock()):
            actual = target.process(self.options)

        self.assertEqual(actual, "Success")
        self.assertEqual(isonom.process.call_count, 0)
        self.assertEqual(loadJson.call_count, 1)
        self.assertEqual(writeCsv.call_count, 1)

    def test_process_step2(self):
        self.options.step = 2
        actual = target.process(self.options)
        self.assertEqual(actual, "Not Implemented")

if __name__ == '__main__':
    unittest.main()
