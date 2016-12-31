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


ONDIR_TEST_DIRECTORY = os.path.join(RESULT_DIRECTORY, 'ondir-test')


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
        reader.extractTags = Mock(return_value={'a': 'b'})
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
    def test_renameFiles_cannot_extract(self, walk):
        reader = Mock()
        reader.extractTags = Mock(return_value={})
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


class TestOnDirectoryLive(unittest.TestCase):
    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def setUp(self):
        self.tree1 = os.path.join(ONDIR_TEST_DIRECTORY, 'alpha', 'beta')
        os.makedirs(self.tree1)
        self.tree2 = os.path.join(ONDIR_TEST_DIRECTORY, 'foo', 'bar')
        os.makedirs(self.tree2)

    def tearDown(self):
        if os.path.exists(ONDIR_TEST_DIRECTORY):
            shutil.rmtree(ONDIR_TEST_DIRECTORY)

    # -------------------------------------------------------------------------

    def _writeAFile(self, path, fileTitle):
        fileName = os.path.join(path, fileTitle)
        with open(fileName, 'w') as f:
            f.write(fileTitle + '\n')
        return fileName

    def _writeReplaceFile(self, fileTitle, source, dest):
        fileName = os.path.join(ONDIR_TEST_DIRECTORY, fileTitle)
        with open(fileName, 'w') as f:
            f.write('{0}\t{1}\n'.format(source, dest))
        return fileName

    # -------------------------------------------------------------------------

    def test_deleteEmptyDirectories_noneEmpty(self):
        file1 = self._writeAFile(self.tree1, 'gamma.txt')
        file2 = self._writeAFile(self.tree2, 'baz.txt')
        success, skipped = target.deleteEmptyDirectories(ONDIR_TEST_DIRECTORY)
        self.assertEqual(success, 0)
        self.assertEqual(skipped, 5)
        self.assertTrue(os.path.exists(file1))
        self.assertTrue(os.path.exists(file2))

    def test_deleteEmptyDirectories_oneEmpty(self):
        file1 = self._writeAFile(self.tree1, 'delta.txt')
        success, skipped = target.deleteEmptyDirectories(ONDIR_TEST_DIRECTORY)
        self.assertEqual(success, 2)
        self.assertEqual(skipped, 3)
        self.assertTrue(os.path.exists(file1))
        self.assertFalse(os.path.exists(self.tree2))

    def test_deleteEmptyDirectories_allEmptyMultilevel(self):
        success, skipped = target.deleteEmptyDirectories(ONDIR_TEST_DIRECTORY)
        self.assertEqual(success, 5)
        self.assertEqual(skipped, 0)
        self.assertFalse(os.path.exists(self.tree1))
        self.assertFalse(os.path.exists(self.tree2))

    def test_deleteFiles_happy(self):
        file1 = self._writeAFile(self.tree1, 'gamma.txt')
        file2 = self._writeAFile(self.tree2, 'baz.mp3')
        success, failed = target.deleteFiles(ONDIR_TEST_DIRECTORY)
        self.assertEqual(success, 2)
        self.assertEqual(failed, 0)
        self.assertTrue(os.path.exists(self.tree1))
        self.assertTrue(os.path.exists(self.tree2))

    @patch('pyTagger.operations.on_directory.os.remove')
    def test_deleteFiles_errors(self, remove):
        remove.side_effect = OSError

        file1 = self._writeAFile(self.tree1, 'gamma.txt')
        file2 = self._writeAFile(self.tree2, 'baz.txt')
        success, failed = target.deleteFiles(ONDIR_TEST_DIRECTORY)
        self.assertEqual(success, 0)
        self.assertEqual(failed, 2)
        self.assertTrue(os.path.exists(file1))
        self.assertTrue(os.path.exists(file2))

    def test_replaceFiles_happy(self):
        file1 = self._writeAFile(self.tree1, 'epsilon.txt')
        file2 = self._writeAFile(self.tree2, 'qaz.txt')
        pairFile = self._writeReplaceFile('updates.txt', file2, file1)

        c = target.replaceFiles(pairFile)

        self.assertEqual(c['replaced'], 1)
        self.assertEqual(c['missing-source'], 0)
        self.assertEqual(c['missing-dest'], 0)
        self.assertEqual(c['errors'], 0)
        self.assertTrue(os.path.exists(file1))
        self.assertFalse(os.path.exists(file2))

        with open(file1) as f:
            contents = f.read()
        self.assertEqual(contents, 'qaz.txt\n')

    def test_replaceFiles_sourceMissing(self):
        file1 = self._writeAFile(self.tree1, 'zeta.txt')
        pairFile = self._writeReplaceFile('updates.txt', 'foo.txt', file1)

        c = target.replaceFiles(pairFile)

        self.assertEqual(c['replaced'], 0)
        self.assertEqual(c['missing-source'], 1)
        self.assertEqual(c['missing-dest'], 0)
        self.assertEqual(c['errors'], 0)
        self.assertTrue(os.path.exists(file1))

    def test_replaceFiles_destMissing(self):
        file2 = self._writeAFile(self.tree2, 'boz.txt')
        pairFile = self._writeReplaceFile('updates.txt', file2, 'foo.txt')

        c = target.replaceFiles(pairFile)

        self.assertEqual(c['replaced'], 0)
        self.assertEqual(c['missing-source'], 0)
        self.assertEqual(c['missing-dest'], 1)
        self.assertEqual(c['errors'], 0)
        self.assertTrue(os.path.exists(file2))

    @patch('pyTagger.operations.on_directory.shutil.move')
    def test_replaceFiles_destPermission(self, move):
        file1 = self._writeAFile(self.tree1, 'theta.txt')
        file2 = self._writeAFile(self.tree2, 'daq.txt')
        pairFile = self._writeReplaceFile('updates.txt', file2, file1)
        move.side_effect = IOError

        c = target.replaceFiles(pairFile)

        self.assertEqual(c['replaced'], 0)
        self.assertEqual(c['missing-source'], 0)
        self.assertEqual(c['missing-dest'], 0)
        self.assertEqual(c['errors'], 1)
        self.assertTrue(os.path.exists(file1))
        self.assertTrue(os.path.exists(file2))

if __name__ == '__main__':
    unittest.main()
