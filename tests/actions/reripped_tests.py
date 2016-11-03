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
        self.keys = ['title', 'album', 'artist', 'track', 'id']
        self.mp3Info = ['bitRate', 'vbr', 'fileHash', 'version']
        with patch.object(sys, 'argv', ['test', '1']):
            self.options = configurationOptions('reripped')

        p = patch('pyTagger.actions.reripped.os.path.exists')
        self.addCleanup(p.stop)
        self.path_exists = p.start()
        self.path_exists.return_value = False

    def test_mergeOne_notOlder_clones(self):
        a = {'title': 'hey'}

        actual = target._mergeOne(a, {})

        self.assertEqual(actual['title'], a['title'])
        a['title'] = 'bar'
        self.assertNotEqual(actual['title'], a['title'])

    def test_mergeOne_notOlder_hasMp3Info(self):
        a = {k: 'foo' for k in ['title'] + self.mp3Info}

        actual = target._mergeOne(a, {})

        for k in ['title', 'id', 'ufid']:
            self.assertTrue(k in actual)
        for k in self.mp3Info:
            self.assertFalse(k in actual)

    def test_mergeOne_allCommonKeys(self):
        a = {k: 'bar' for k in self.keys}
        b = {k: 'foo' for k in self.keys}

        actual = target._mergeOne(a, b)

        self.assertEqual(len(actual), len(self.keys))
        for k in self.keys:
            self.assertEqual(actual[k], b[k])

    def test_mergeOne_allCommonKeys_olderIsNull(self):
        a = {k: 'bar' for k in self.keys}
        b = {k: '' for k in self.keys}

        actual = target._mergeOne(a, b)

        self.assertEqual(len(actual), len(self.keys))
        for k in self.keys:
            self.assertEqual(actual[k], a[k])

    def test_mergeOne_noCommonKeys(self):
        a = {k: 'baz' for k in ['title', 'album', 'artist']}
        b = {k: 'baz' for k in ['track', 'id']}

        actual = target._mergeOne(a, b)

        self.assertEqual(len(actual), len(self.keys))
        for k in self.keys:
            self.assertEqual(actual[k], 'baz')

    def test_mergeOne_addsUfid(self):
        keys = ['title', 'album']
        a = {k: 'bar' for k in keys}
        b = {k: 'foo' for k in keys}

        actual = target._mergeOne(a, b)

        self.assertTrue('id' in actual)
        self.assertTrue('ufid' in actual)
        self.assertTrue('DJTagger' in actual['ufid'])
        self.assertEqual(actual['id'], actual['ufid']['DJTagger'])

    def test_mergeOne_clones(self):
        a = {k: 'bar' for k in self.keys}
        b = {k: 'foo' for k in self.keys}

        actual = target._mergeOne(a, b)

        for k in self.keys:
            a[k] = 'qaz'
            b[k] = 'baz'
            self.assertEqual(actual[k], 'foo')

    def test_mergeOne_hasMp3Info(self):
        a = {k: 'bar' for k in self.keys}
        b = {k: 'foo' for k in self.mp3Info}

        actual = target._mergeOne(a, b)

        self.assertEqual(len(actual), len(self.keys))
        for k in self.mp3Info:
            self.assertFalse(k in actual)

    @patch('pyTagger.actions.reripped.saveJsonIncrementalDict')
    @patch('pyTagger.actions.reripped.loadJson')
    def test_mergeAll(self, loadJson, saveJson):
        def noop_coroutine(file, compact):
            for i in [0, 1, 2, 3, 4, len(self.keys)]:
                k, v = yield i
                self.assertEqual(k, '/foo/bar')
                self.assertEqual(v, 'baz')

        loadJson.return_value = [
            {'newTags': 'foo', 'oldTags': 'bar', 'newPath': '/foo/bar'},
            {'newTags': 'foo', 'oldTags': 'bar', 'newPath': '/foo/bar'}
        ]
        saveJson.side_effect = noop_coroutine

        mergeOne = Mock(return_value='baz')
        with patch.object(target, '_mergeOne', mergeOne):
            actual = target._mergeAll(self.options)

        self.assertEqual(loadJson.call_count, 1)
        self.assertEqual(mergeOne.call_count, 2)
        self.assertEqual(mergeOne.call_args[0], ('foo', 'bar'))
        self.assertEqual(saveJson.call_count, 1)
        self.assertEqual(actual, 2)

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
