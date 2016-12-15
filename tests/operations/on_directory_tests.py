from __future__ import unicode_literals
import unittest
import io
import os
import shutil
import sys
import pyTagger.operations.on_directory as target
from collections import Counter
from tests import *
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


class FakeFile(io.StringIO):
    def __iter__(self):
        yield 'foo.mp3'
        yield 'bar.txt'

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class TestOnDirectory(unittest.TestCase):

    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    # Walk Variations

    @patch('pyTagger.operations.on_directory._walkDirectory')
    @patch('pyTagger.operations.on_directory.os')
    def test_walk_directory(self, os, innerWalk):
        expected = ['alpha', 'beta', 'gamma']
        os.path.isdir.return_value = True
        os.path.isfile.return_value = False
        innerWalk.return_value = expected

        actual = list(target.walk('foo'))

        self.assertEqual(actual, expected)
        innerWalk.assert_called_with('foo', target._filterMp3s)

    @patch('pyTagger.operations.on_directory._walkFile')
    @patch('pyTagger.operations.on_directory.os')
    def test_walk_file(self, os, innerWalk):
        expected = ['alpha', 'beta', 'gamma']
        os.path.isdir.return_value = False
        os.path.isfile.return_value = True
        innerWalk.return_value = expected

        actual = list(target.walk('foo'))

        self.assertEqual(actual, expected)
        innerWalk.assert_called_with('foo', target._filterMp3s)

    def test_walk_unknown(self):
        with self.assertRaises(ValueError):
            _ = list(target.walk('foo'))

    @patch('pyTagger.operations.on_directory._walkDirectory')
    @patch('pyTagger.operations.on_directory.os')
    def test_walkAll_directory(self, os, innerWalk):
        expected = ['alpha', 'beta', 'gamma']
        os.path.isdir.return_value = True
        os.path.isfile.return_value = False
        innerWalk.return_value = expected

        actual = list(target.walkAll('foo'))

        self.assertEqual(actual, expected)
        innerWalk.assert_called_with('foo', target._filterAll)

    @patch('pyTagger.operations.on_directory._walkFile')
    @patch('pyTagger.operations.on_directory.os')
    def test_walkAll_file(self, os, innerWalk):
        expected = ['alpha', 'beta', 'gamma']
        os.path.isdir.return_value = False
        os.path.isfile.return_value = True
        innerWalk.return_value = expected

        actual = list(target.walkAll('foo'))

        self.assertEqual(actual, expected)
        innerWalk.assert_called_with('foo', target._filterAll)

    def test_walkAll_unknown(self):
        with self.assertRaises(ValueError):
            _ = list(target.walkAll('foo'))

    # -------------------------------------------------------------------------
    # Local Helper

    def test_needsMove_bothEqual(self):
        current = '/path/to/01-11- Restart.mp3'
        actual = target.needsMove(current, current)
        self.assertEqual(False, actual)

    @patch('pyTagger.operations.on_directory.os.path.exists')
    def test_needsMove_collision(self, mocked):
        mocked.return_value = True
        proposed = '/path/to/01-11- Restart.mp3'
        with self.assertRaises(ValueError):
            target.needsMove('foo', proposed)

    def test_needsMove_notEqual(self):
        current = '/path/to/foo.mp3'
        proposed = '/path/to/01-11- Restart.mp3'
        actual = target.needsMove(current, proposed)
        self.assertEqual(True, actual)

    # -------------------------------------------------------------------------
    # Directory Functions

    @patch('pyTagger.operations.on_directory.hashFile')
    @patch('pyTagger.operations.on_directory.walkAll')
    def test_buildHashTable(self, walk, hashFile):
        walk.return_value = ['foo', 'bar', 'baz', 'qaz']
        hashFile.return_value = '1234567890'

        actual = target.buildHashTable('blah')
        walk.assert_called_with('blah')
        self.assertEqual(hashFile.call_count, 4)
        for v in actual.values():
            self.assertEqual(v, 'qaz')

    @patch('pyTagger.operations.on_directory.singleExtract')
    @patch('pyTagger.operations.on_directory.walk')
    @patch('pyTagger.operations.on_directory.os')
    def test_extractImages_path_doesnt_exist(self, os, walk, extract):
        os.path.exists.return_value = False
        walk.return_value = ['a']
        extract.return_value = Counter()

        actual = target.extractImages('foo', 'bar', 'baz')

        os.path.exists.assert_called_with('bar')
        os.makedirs.assert_called_with('bar')
        walk.assert_called_with('foo')
        self.assertEqual(extract.call_count, 1)
        self.assertEqual(actual, {})

    @patch('pyTagger.operations.on_directory.singleExtract')
    @patch('pyTagger.operations.on_directory.buildHashTable')
    @patch('pyTagger.operations.on_directory.walk')
    @patch('pyTagger.operations.on_directory.os')
    def test_extractImages_path_exists(self, os, walk, buildHash, extract):
        os.path.exists.return_value = True
        buildHash.return_value = '1234567890'
        walk.return_value = ['a']
        extract.return_value = Counter()

        actual = target.extractImages('foo', 'bar', 'baz')

        os.path.exists.assert_called_with('bar')
        os.makedirs.assert_not_called()
        buildHash.assert_called_with('bar')
        walk.assert_called_with('foo')
        self.assertEqual(extract.call_count, 1)
        self.assertEqual(actual, {})

    @patch('pyTagger.operations.on_directory.needsMove')
    @patch('pyTagger.operations.on_directory.shutil.move')
    @patch('pyTagger.operations.on_directory.buildPath')
    @patch('pyTagger.operations.on_directory.walk')
    @patch('pyTagger.operations.on_directory.os')
    def test_renameFiles_happyPath(self, os, walk, buildPath, move, needsMove):
        reader = Mock()
        reader.extractTags = Mock(return_value='{}')
        walk.return_value = ['a']
        buildPath.return_value = ['foo', 'bar', 'baz']
        needsMove.return_value = True
        os.path.exists.return_value = True

        c = target.renameFiles('/path/one', '/path/two', reader)
        self.assertEqual(c['moved'], 1)
        self.assertEqual(c['skipped'], 0)
        self.assertEqual(c['errors'], 0)
        self.assertEqual(c['collisions'], 0)

    @patch('pyTagger.operations.on_directory.needsMove')
    @patch('pyTagger.operations.on_directory.shutil.move')
    @patch('pyTagger.operations.on_directory.buildPath')
    @patch('pyTagger.operations.on_directory.walk')
    def test_renameFiles_skip(self, walk, buildPath, move, needsMove):
        reader = Mock()
        reader.extractTags = Mock(return_value='{}')
        walk.return_value = ['a']
        buildPath.return_value = ['foo', 'bar', 'baz']
        needsMove.return_value = False

        c = target.renameFiles('/path/one', '/path/two', reader)
        self.assertEqual(c['moved'], 0)
        self.assertEqual(c['skipped'], 1)
        self.assertEqual(c['errors'], 0)
        self.assertEqual(c['collisions'], 0)

    @patch('pyTagger.operations.on_directory.walk')
    def test_renameFiles_readonly_destination(self, walk):
        reader = Mock()
        reader.extractTags = Mock(side_effect=OSError)
        walk.return_value = ['a']

        c = target.renameFiles('/path/one', '/path/two', reader)
        self.assertEqual(c['moved'], 0)
        self.assertEqual(c['skipped'], 0)
        self.assertEqual(c['errors'], 1)
        self.assertEqual(c['collisions'], 0)

    @patch('pyTagger.operations.on_directory.walk')
    def test_renameFiles_collision(self, walk):
        reader = Mock()
        reader.extractTags = Mock(side_effect=ValueError)
        walk.return_value = ['a']

        c = target.renameFiles('/path/one', '/path/two', reader)
        self.assertEqual(c['moved'], 0)
        self.assertEqual(c['skipped'], 0)
        self.assertEqual(c['errors'], 0)
        self.assertEqual(c['collisions'], 1)


if __name__ == '__main__':
    unittest.main()
