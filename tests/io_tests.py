import unittest
from pyTagger.io import toAbsolute, loadJson
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestIO(unittest.TestCase):
    @patch('pyTagger.io.os.path.dirname')
    def test_toAbsolute(self, dirname):
        path = 'foo.txt'
        dirname.return_value = '/bar/baz/qaz/'

        actual = toAbsolute(path)
        self.assertEqual(actual, '/bar/baz/qaz/foo.txt')

    def test_loadJson(self):
        absPath = toAbsolute('../tests/utf8.json')

        snapshot = loadJson(absPath)
        self.assertEqual(len(snapshot), 1)
        k, v = snapshot.popitem()
        self.assertEqual(v['artist'], u'T\u00e9l\u00e9popmusik')

if __name__ == '__main__':
    unittest.main()
