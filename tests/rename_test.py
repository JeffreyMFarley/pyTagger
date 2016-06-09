import unittest
import os
import sys
import shutil
import random
import uuid
import binascii
import itertools
import pyTagger
from tests import *

RENAMED_DIRECTORY = os.path.join(RESULT_DIRECTORY, 'renamed')

class TestRename(unittest.TestCase):

    def setUp(self):
        assert sys.version < '3', 'This test must be run in Python 2.x'
        self.target = pyTagger.Rename(RENAMED_DIRECTORY)

    def _buildTags(self, **kwargs):
        t =  {
        'album': u'Bar', 
        'artist': u'Foo (with Qaz)', 
        'track': 1, 
        'totalTrack': 14, 
        'compilation': None,
        'title': u'Baz',
        'albumArtist': u'Foo', 
        'totalDisc': 1, 
        'disc': 1}
        t.update(**kwargs)
        return t

    def test_buildPath_badChars(self):
        tags = self._buildTags(title=r'\/:*?"<>|.')
        expected = ['Foo', 'Bar', '01 - __________.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_compilation(self):
        tags = self._buildTags(compilation=1)
        expected = ['Compilations', 'Bar', '01 - Baz.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_disc(self):
        tags = self._buildTags(totalDisc=2)
        expected = ['Foo', 'Bar', '01-01 - Baz.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_disc2(self):
        tags = self._buildTags(totalDisc=2, disc=2)
        expected = ['Foo', 'Bar', '02-01 - Baz.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_exception_emptyAlbum(self):
        tags = self._buildTags()
        del tags['album']
        with self.assertRaises(ValueError):
            self.target.buildPath(tags)

    def test_buildPath_exception_emptyArtist(self):
        tags = self._buildTags()
        del tags['albumArtist']
        with self.assertRaises(ValueError):
            self.target.buildPath(tags)

    def test_buildPath_exception_emptyTitle(self):
        tags = self._buildTags()
        del tags['title']
        with self.assertRaises(ValueError):
            self.target.buildPath(tags)

    def test_buildPath_exception_emptyTrack(self):
        tags = self._buildTags()
        del tags['track']
        expected = ['Foo', 'Bar', '00 - Baz.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_happy(self):
        tags = self._buildTags()
        expected = ['Foo', 'Bar', '01 - Baz.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_length_album(self):
        s = '0123456789abcdef' * 4
        tags = self._buildTags(album=s)
        expected = ['Foo', '0123456789abcdef0123456789abcdef01234567', 
                    '01 - Baz.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_length_artist(self):
        s = '0123456789abcdef' * 4
        tags = self._buildTags(albumArtist=s)
        expected = ['0123456789abcdef0123456789abcdef01234567', 'Bar',
                    '01 - Baz.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_length_title(self):
        s = '0123456789abcdef' * 4
        tags = self._buildTags(title=s)
        expected = ['Foo', 'Bar', 
                    '01 - 0123456789abcdef0123456789ab.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_length_title_disc(self):
        s = '0123456789abcdef' * 4
        tags = self._buildTags(title=s, totalDisc=2)
        expected = ['Foo', 'Bar', 
                    '01-01 - 0123456789abcdef012345678.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_matchExtension(self):
        tags = self._buildTags()
        expected = ['Foo', 'Bar', '01 - Baz.MP3']
        actual = self.target.buildPath(tags, 'MP3')
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_trim(self):
        tags = self._buildTags(title=' B a z ', album=' B a r ', 
                               albumArtist=' F o o ')
        expected = ['F o o', 'B a r', '01 - B a z.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()