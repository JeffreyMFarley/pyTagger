from __future__ import unicode_literals
import io
import unittest
import pyTagger.actions.reripped as target
from nose_parameterized import parameterized
from pyTagger.utils import configurationOptions
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


class FakeFile(io.StringIO):
    def __exit__(self, exc_type, exc_value, traceback):
        self.seek(0)

interview = [
    {
        'newTags': 'foo', 'newPath': '/foo/bar',
        'oldTags': 'bar', 'oldPath': '/buzz/bar',
        'status': 'manual'
    },
    {
        'newTags': 'foo', 'newPath': '/foo/baz',
        'oldTags': 'bar', 'oldPath': '/buzz/baz',
        'status': 'ready'
    },
    {
        'newTags': 'foo', 'newPath': '/foo/qaz',
        'oldTags': 'bar', 'oldPath': '/buzz/qaz',
        'status': 'manual'
    }
]


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

        loadJson.return_value = interview
        generateUfid.return_value = ufid
        union.side_effect = [{}, {}, {}]
        expected = {
            '/foo/bar': {'id': ufid, 'ufid': {'DJTagger': ufid}},
            '/foo/baz': {},
            '/foo/qaz': {'id': ufid, 'ufid': {'DJTagger': ufid}}
        }

        actual = target._mergeAll(self.options)

        self.assertEqual(loadJson.call_count, 1)
        self.assertEqual(union.call_count, 3)
        self.assertEqual(union.call_args[0], ('foo', 'bar'))
        self.assertEqual(generateUfid.call_count, 2)
        self.assertEqual(actual, expected)

    @patch('pyTagger.actions.reripped.writeCsv')
    @patch('pyTagger.actions.reripped.loadJson')
    @patch('pyTagger.actions.reripped.tag_album')
    def test_process_tag_album_success(self, tag_album, loadJson, writeCsv):
        tag_album.process.return_value = "Success"
        actual = target._tagAlbum(self.options)
        self.assertEqual(actual, "Success")
        self.assertEqual(loadJson.call_count, 1)
        self.assertEqual(writeCsv.call_count, 1)

    @patch('pyTagger.actions.reripped.writeCsv')
    @patch('pyTagger.actions.reripped.loadJson')
    @patch('pyTagger.actions.reripped.tag_album')
    def test_process_tag_album_fails(self, tag_album, loadJson, writeCsv):
        tag_album.process.return_value = "Foo"
        actual = target._tagAlbum(self.options)
        self.assertEqual(actual, "Foo")
        self.assertEqual(loadJson.call_count, 0)
        self.assertEqual(writeCsv.call_count, 0)

    @patch('pyTagger.actions.reripped._tagAlbum')
    def test_process_step1_album_file_exists(self, tagAlbum):
        self.path_exists.side_effect = [False, True]
        tagAlbum.return_value = "Foo"
        actual = target._step1(self.options)
        self.assertEqual(actual, "Foo")
        self.assertEqual(tagAlbum.call_count, 1)

    @patch('pyTagger.actions.reripped._tagAlbum')
    @patch('pyTagger.actions.reripped.saveJson')
    @patch('pyTagger.actions.reripped.isonom')
    def test_process_step1_isonom_ok(self, isonom, saveJson, tagAlbum):
        self.path_exists.side_effect = [False, False]
        isonom.process.return_value = "Success"
        tagAlbum.return_value = "Foo"
        with patch.object(target, '_mergeAll', Mock()):
            actual = target._step1(self.options)

        self.assertEqual(actual, "Foo")
        self.assertEqual(isonom.process.call_count, 1)
        self.assertEqual(saveJson.call_count, 1)
        self.assertEqual(tagAlbum.call_count, 1)

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

    # -------------------------------------------------------------------------

    def test_buildDeletes(self):
        snapshot = {'/foo/baz': {}}
        expected = ['/foo/bar', '/foo/qaz']
        actual = target._buildDeletes(interview, snapshot)
        self.assertEqual(actual, expected)

    def test_buildMoves(self):
        expected = ['/foo/bar', '/foo/qaz']
        actual = target._buildMoves(interview)
        self.assertEqual(actual, expected)

    def test_buildUpdates(self):
        expected = [('/foo/baz', '/buzz/baz')]
        actual = target._buildUpdates(interview)
        self.assertEqual(actual, expected)

    def test_writeText(self):
        output = FakeFile()
        with patch.object(io, 'open') as fmocked:
            fmocked.return_value = output
            target._writeText(['a', 'b', 'c'], 'foo.txt')

        actual = output.getvalue()
        self.assertEqual(actual, 'a\nb\nc')

        actual = [l for l in output]
        output.close()
        self.assertEqual(len(actual), 3)

    def test_process_step2_needs_csv(self):
        self.options.step = 2
        actual = target.process(self.options)
        self.assertEqual(actual, "Not Ready")

    @patch('pyTagger.actions.reripped.extractImages')
    @patch('pyTagger.actions.reripped.updateFromSnapshot')
    @patch('pyTagger.actions.reripped.ID3Proxy')
    @patch('pyTagger.actions.reripped.loadJson')
    @patch('pyTagger.actions.reripped.convert')
    def test_process_step2a(self, convert, loadJson, id3, update, extract):
        snapshot = {'/foo/bar': {}, '/foo/baz': {}}

        self.path_exists.side_effect = [True, False]
        loadJson.side_effect = [interview, snapshot]
        update.return_value = (99, 13)
        extract.return_value = {}

        output = FakeFile()
        with patch.object(io, 'open') as fmocked:
            fmocked.return_value = output
            target._step2(self.options)

        self.assertEqual(convert.call_count, 1)
        self.assertEqual(loadJson.call_count, 2)
        self.assertEqual(id3.call_count, 1)
        self.assertEqual(update.call_count, 1)
        self.assertEqual(extract.call_count, 1)

    @patch('pyTagger.actions.reripped.extractImages')
    @patch('pyTagger.actions.reripped.updateFromSnapshot')
    @patch('pyTagger.actions.reripped.ID3Proxy')
    @patch('pyTagger.actions.reripped.loadJson')
    @patch('pyTagger.actions.reripped.convert')
    def test_process_step2b(self, convert, loadJson, id3, update, extract):
        snapshot = {'/foo/bar': {}, '/foo/baz': {}}

        self.path_exists.side_effect = [True, True]
        loadJson.side_effect = [interview, snapshot]
        update.return_value = (99, 13)
        extract.return_value = {}

        output = FakeFile()
        with patch.object(io, 'open') as fmocked:
            fmocked.return_value = output
            target._step2(self.options)

        self.assertEqual(convert.call_count, 0)
        self.assertEqual(loadJson.call_count, 2)
        self.assertEqual(id3.call_count, 1)
        self.assertEqual(update.call_count, 1)
        self.assertEqual(extract.call_count, 1)

    # -------------------------------------------------------------------------

    def test_deleteFiles_no_file(self):
        actual = target._deleteFiles(self.options)
        self.assertEqual(actual, True)

    @patch('pyTagger.actions.reripped.os.remove')
    @patch('pyTagger.actions.reripped.deleteFiles')
    @patch('pyTagger.actions.reripped.os.path.exists')
    def test_deleteFiles_success(self, exists, deleteFiles, remove):
        self.options.cleanup = True
        self.options.to_delete = 'foo.txt'
        exists.return_value = True
        deleteFiles.return_value = (99, 0)
        actual = target._deleteFiles(self.options)
        self.assertEqual(actual, True)
        remove.assert_called_with('foo.txt')

    @patch('pyTagger.actions.reripped.os.remove')
    @patch('pyTagger.actions.reripped.deleteFiles')
    @patch('pyTagger.actions.reripped.os.path.exists')
    def test_deleteFiles_errors(self, exists, deleteFiles, remove):
        self.options.cleanup = True
        self.options.to_delete = 'foo.txt'
        exists.return_value = True
        deleteFiles.return_value = (99, 1)
        actual = target._deleteFiles(self.options)
        self.assertEqual(actual, False)
        self.assertEqual(remove.call_count, 0)

    def test_moveFiles_no_file(self):
        actual = target._moveFiles(self.options)
        self.assertEqual(actual, True)

    @patch('pyTagger.actions.reripped.os.remove')
    @patch('pyTagger.actions.reripped.renameFiles')
    @patch('pyTagger.actions.reripped.os.path.exists')
    def test_moveFiles_success(self, exists, renameFiles, remove):
        self.options.cleanup = True
        self.options.to_move = 'foo.txt'
        exists.return_value = True
        renameFiles.return_value = {'moved': 13}
        actual = target._moveFiles(self.options)
        self.assertEqual(actual, True)
        remove.assert_called_with('foo.txt')

    @patch('pyTagger.actions.reripped.os.remove')
    @patch('pyTagger.actions.reripped.renameFiles')
    @patch('pyTagger.actions.reripped.os.path.exists')
    def test_moveFiles_errors(self, exists, renameFiles, remove):
        self.options.cleanup = True
        self.options.to_move = 'foo.txt'
        exists.return_value = True
        renameFiles.return_value = {'moved': 13, 'foo': 2}
        actual = target._moveFiles(self.options)
        self.assertEqual(actual, False)
        self.assertEqual(remove.call_count, 0)

    def test_replaceFiles_no_file(self):
        actual = target._replaceFiles(self.options)
        self.assertEqual(actual, True)

    @patch('pyTagger.actions.reripped.os.remove')
    @patch('pyTagger.actions.reripped.replaceFiles')
    @patch('pyTagger.actions.reripped.os.path.exists')
    def test_replaceFiles_success(self, exists, replaceFiles, remove):
        self.options.cleanup = True
        self.options.to_update = 'foo.txt'
        exists.return_value = True
        replaceFiles.return_value = {'replaced': 13}
        actual = target._replaceFiles(self.options)
        self.assertEqual(actual, True)
        remove.assert_called_with('foo.txt')

    @patch('pyTagger.actions.reripped.os.remove')
    @patch('pyTagger.actions.reripped.replaceFiles')
    @patch('pyTagger.actions.reripped.os.path.exists')
    def test_replaceFiles_errors(self, exists, replaceFiles, remove):
        self.options.cleanup = True
        self.options.to_update = 'foo.txt'
        exists.return_value = True
        replaceFiles.return_value = {'replaced': 13, 'foo': 2}
        actual = target._replaceFiles(self.options)
        self.assertEqual(actual, False)
        self.assertEqual(remove.call_count, 0)

    @patch('pyTagger.actions.reripped.askMultipleChoice')
    def test_process_step3_not_ready(self, ask):
        self.options.step = 3
        ask.return_value = 'N'

        actual = target.process(self.options)
        self.assertEqual(actual, 'Not Ready')

    @parameterized.expand([
        (True, True, True, 'Success'),
        (True, True, False, 'Not Completed'),
        (True, False, True, 'Not Completed')
    ])
    @patch('pyTagger.actions.reripped.os.remove')
    @patch('pyTagger.actions.reripped._replaceFiles')
    @patch('pyTagger.actions.reripped._moveFiles')
    @patch('pyTagger.actions.reripped._deleteFiles')
    @patch('pyTagger.actions.reripped.askMultipleChoice')
    def test_process_step3(self, r0, r1, r2, expect, ask, df, mf, rf, remove):
        self.options.step = 3
        self.options.cleanup = r2
        ask.return_value = 'Y'
        df.return_value = r0
        mf.return_value = r1
        rf.return_value = r2

        actual = target.process(self.options)
        self.assertEqual(actual, expect)

        if expect == 'Success':
            self.assertEqual(remove.call_count, 3)
        else:
            self.assertEqual(remove.call_count, 0)

    # -------------------------------------------------------------------------

    def test_process_step4(self):
        self.options.step = 4
        actual = target.process(self.options)
        self.assertEqual(actual, "Not Implemented")

if __name__ == '__main__':
    unittest.main()
