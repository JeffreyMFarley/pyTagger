from __future__ import unicode_literals
import unittest
import pyTagger.operations.hash as target


class TestHash(unittest.TestCase):
    def test_hashFile_badfile(self):
        actual = target.hashFile('foo.mp3')
        self.assertEqual(actual, '')

if __name__ == '__main__':
    unittest.main()
