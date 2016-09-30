import unittest
import os
import shutil
import itertools
import pyTagger
from tests import *
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

RENAMED_DIRECTORY = os.path.join(RESULT_DIRECTORY, u'renamed', '')
CHECKIN_DIRECTORY = os.path.join(SOURCE_DIRECTORY, u'Checkin')

# -----------------------------------------------------------------------------
# Module-Wide Routines
# -----------------------------------------------------------------------------


def resetFile(fileName):
    if not os.path.exists(RENAMED_DIRECTORY):
        os.makedirs(RENAMED_DIRECTORY)

    fromFile = os.path.join(CHECKIN_DIRECTORY, fileName)
    shutil.copy(fromFile, RENAMED_DIRECTORY)
    return os.path.join(RENAMED_DIRECTORY, fileName)


def setUpModule():
    pass


def tearDownModule():
    #shutil.rmtree(unicode(RENAMED_DIRECTORY))
    pass

# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------


class TestRename(unittest.TestCase):

    def setUp(self):
        targetDir = os.path.join(RESULT_DIRECTORY, u'renamed')
        self.target = pyTagger.Rename(targetDir)

    def _buildTags(self, **kwargs):
        t = {
            'album': u'Bar',
            'artist': u'Foo (with Qaz)',
            'track': 1,
            'totalTrack': 14,
            'compilation': None,
            'title': u'Baz',
            'albumArtist': u'Foo',
            'totalDisc': 1,
            'disc': 1
        }
        t.update(**kwargs)
        return t

    def test_buildPath_badChars(self):
        tags = self._buildTags(title=u'a\\/:*?"<>|.')
        expected = [u'Foo', u'Bar', u'01 a.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_compilation(self):
        tags = self._buildTags(compilation=1)
        expected = [u'Compilations', u'Bar', u'01 Baz.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_disc(self):
        tags = self._buildTags(totalDisc=2)
        expected = [u'Foo', u'Bar', u'01-01 Baz.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_disc2(self):
        tags = self._buildTags(totalDisc=2, disc=2)
        expected = [u'Foo', u'Bar', u'02-01 Baz.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_exception_emptyAlbum(self):
        tags = self._buildTags()
        del tags['album']
        with self.assertRaises(ValueError):
            self.target.buildPath(tags)

    def test_buildPath_exception_emptyAlbumArtist(self):
        tags = self._buildTags()
        del tags['albumArtist']
        expected = [u'Foo (with Qaz)', u'Bar', u'01 Baz.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_exception_emptyArtist(self):
        tags = self._buildTags()
        del tags['albumArtist']
        del tags['artist']
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
        expected = [u'Foo', u'Bar', u'00 Baz.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_happy(self):
        tags = self._buildTags()
        expected = [u'Foo', u'Bar', u'01 Baz.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_length_album(self):
        s = u'0123456789abcdef' * 4
        tags = self._buildTags(album=s)
        expected = [u'Foo', u'0123456789abcdef0123456789abcdef01234567',
                    u'01 Baz.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_length_artist(self):
        s = u'0123456789abcdef' * 4
        tags = self._buildTags(albumArtist=s)
        expected = [u'0123456789abcdef0123456789abcdef01234567', u'Bar',
                    u'01 Baz.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_length_title(self):
        s = u'0123456789abcdef' * 4
        tags = self._buildTags(title=s)
        expected = [u'Foo', u'Bar',
                    u'01 0123456789abcdef0123456789abcdef0.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_length_title_disc(self):
        s = u'0123456789abcdef' * 4
        tags = self._buildTags(title=s, totalDisc=2)
        expected = [u'Foo', u'Bar',
                    u'01-01 0123456789abcdef0123456789abcd.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_matchExtension(self):
        tags = self._buildTags()
        expected = [u'Foo', u'Bar', u'01 Baz.MP3']
        actual = self.target.buildPath(tags, 'MP3')
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_trim(self):
        tags = self._buildTags(title=u' B a z ', album=u' B a r ',
                               albumArtist=u' F o o ')
        expected = [u'F o o', u'B a r', u'01 B a z.mp3']
        actual = self.target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_needsMove_bothEqual(self):
        current = resetFile(u'01-11- Restart.mp3')
        actual = self.target.needsMove(current, current)
        self.assertEqual(False, actual)

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    @patch('pyTagger.rename.os.path.exists')
    def test_needsMove_collision(self, mocked):
        mocked.return_value = True
        proposed = resetFile(u'01-11- Restart.mp3')
        with self.assertRaises(ValueError):
            self.target.needsMove(u'foo', proposed)

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_needsMove_notEqual(self):
        current = resetFile(u'01-11- Restart.mp3')
        proposed = os.path.join(RENAMED_DIRECTORY, u'foo.mp3')
        actual = self.target.needsMove(current, proposed)
        self.assertEqual(True, actual)

if __name__ == '__main__':
    unittest.main()
