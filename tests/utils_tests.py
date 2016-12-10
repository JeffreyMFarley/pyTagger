from __future__ import unicode_literals
import unittest
import io
import os
import pyTagger.utils as target
from tests import *
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestIO(unittest.TestCase):
    @patch('pyTagger.utils.os.path.dirname')
    def test_toAbsolute(self, dirname):
        path = 'foo.txt'
        dirname.return_value = '/bar/baz/qaz/'

        actual = target.toAbsolute(path)
        self.assertEqual(actual, '/bar/baz/qaz/foo.txt')

    def test_loadJson(self):
        absPath = target.toAbsolute('../tests/utf8.json')

        snapshot = target.loadJson(absPath)
        self.assertEqual(len(snapshot), 1)
        k, v = snapshot.popitem()
        self.assertEqual(v['artist'], 'T\u00e9l\u00e9popmusik')

    @unittest.skipUnless(sampleFilesExist, 'No results directory to use')
    def test_saveJson(self):
        outFile = os.path.join(RESULT_DIRECTORY, r'foo.json')
        absPath = target.toAbsolute('../tests/utf8.json')
        expected = target.loadJson(absPath)

        target.saveJson(outFile, expected)
        actual = target.loadJson(outFile)
        self.assertEqual(actual, expected)

    def test_saveJsonIncrementalArray(self):
        output = io.StringIO()
        with patch.object(io, 'open') as fmocked:
            fmocked.return_value = output
            gen = target.saveJsonIncrementalArray('foo.json')
            row = next(gen)
            self.assertEqual(row, 0)
            self.assertEqual(output.getvalue(), '[')
            row = gen.send('T\u00e9l\u00e9popmusik')
            self.assertEqual(row, 1)
            self.assertEqual(output.getvalue(), '[\n"T\u00e9l\u00e9popmusik"')
            gen.close()

    def test_saveJsonIncrementalDict(self):
        output = io.StringIO()
        with patch.object(io, 'open') as fmocked:
            fmocked.return_value = output
            gen = target.saveJsonIncrementalDict('foo.json')
            row = next(gen)
            self.assertEqual(row, 0)
            self.assertEqual(output.getvalue(), '{')
            row = gen.send(('key', 'T\u00e9l\u00e9popmusik'))
            self.assertEqual(row, 1)
            self.assertEqual(output.getvalue(),
                             '{\n"key":\n"T\u00e9l\u00e9popmusik"')
            gen.close()

    def test_needsMove_bothEqual(self):
        current = '/path/to/01-11- Restart.mp3'
        actual = target.needsMove(current, current)
        self.assertEqual(False, actual)

    @patch('pyTagger.utils.os.path.exists')
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

if __name__ == '__main__':
    unittest.main()
