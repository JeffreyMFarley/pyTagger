from __future__ import unicode_literals
import unittest
import io
import pyTagger.utils as target
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

if __name__ == '__main__':
    unittest.main()
