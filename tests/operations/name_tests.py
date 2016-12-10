from __future__ import unicode_literals
import unittest
import pyTagger.operations.name as target


class TestName(unittest.TestCase):
    def setUp(self):
        self.data = {
            'album': 'Foo',
            'artist': 'Bar',
            'title': 'Baz'
        }

    def _buildTags(self, **kwargs):
        t = {
            'album': 'Bar',
            'artist': 'Foo (with Qaz)',
            'track': 1,
            'totalTrack': 14,
            'compilation': None,
            'title': 'Baz',
            'albumArtist': 'Foo',
            'totalDisc': 1,
            'disc': 1
        }
        t.update(**kwargs)
        return t

    def test_albumArtistTitle_happy(self):
        actual = target._albumArtistTitle(self.data)
        self.assertEqual(actual, ('Foo', 'Bar', 'Baz'))

    def test_albumArtistTitle_noAlbum(self):
        del self.data['album']
        with self.assertRaises(ValueError):
            target._albumArtistTitle(self.data)

    def test_albumArtistTitle_noArtist(self):
        del self.data['artist']
        with self.assertRaises(ValueError):
            target._albumArtistTitle(self.data)

    def test_albumArtistTitle_AlbumArtist(self):
        del self.data['artist']
        self.data['albumArtist'] = 'Qaz'
        actual = target._albumArtistTitle(self.data)
        self.assertEqual(actual, ('Foo', 'Qaz', 'Baz'))

    def test_albumArtistTitle_Compliation(self):
        del self.data['artist']
        self.data['compilation'] = True
        actual = target._albumArtistTitle(self.data)
        self.assertEqual(actual, ('Foo', 'Compilations', 'Baz'))

    def test_albumArtistTitle_noTitle(self):
        del self.data['title']
        with self.assertRaises(ValueError):
            target._albumArtistTitle(self.data)

    def test_buildPath_badChars(self):
        tags = self._buildTags(title='a\\/:*?"<>|.')
        expected = ['Foo', 'Bar', '01 a.mp3']
        actual = target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_compilation(self):
        tags = self._buildTags(compilation=1)
        expected = ['Compilations', 'Bar', '01 Baz.mp3']
        actual = target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_disc(self):
        tags = self._buildTags(totalDisc=2)
        expected = ['Foo', 'Bar', '01-01 Baz.mp3']
        actual = target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_disc2(self):
        tags = self._buildTags(totalDisc=2, disc=2)
        expected = ['Foo', 'Bar', '02-01 Baz.mp3']
        actual = target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_exception_emptyAlbum(self):
        tags = self._buildTags()
        del tags['album']
        with self.assertRaises(ValueError):
            target.buildPath(tags)

    def test_buildPath_exception_emptyAlbumArtist(self):
        tags = self._buildTags()
        del tags['albumArtist']
        expected = ['Foo (with Qaz)', 'Bar', '01 Baz.mp3']
        actual = target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_exception_emptyArtist(self):
        tags = self._buildTags()
        del tags['albumArtist']
        del tags['artist']
        with self.assertRaises(ValueError):
            target.buildPath(tags)

    def test_buildPath_exception_emptyTitle(self):
        tags = self._buildTags()
        del tags['title']
        with self.assertRaises(ValueError):
            target.buildPath(tags)

    def test_buildPath_exception_emptyTrack(self):
        tags = self._buildTags()
        del tags['track']
        expected = ['Foo', 'Bar', '00 Baz.mp3']
        actual = target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_happy(self):
        tags = self._buildTags()
        expected = ['Foo', 'Bar', '01 Baz.mp3']
        actual = target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_length_album(self):
        s = '0123456789abcdef' * 4
        tags = self._buildTags(album=s)
        expected = ['Foo', '0123456789abcdef0123456789abcdef01234567',
                    '01 Baz.mp3']
        actual = target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_length_artist(self):
        s = '0123456789abcdef' * 4
        tags = self._buildTags(albumArtist=s)
        expected = ['0123456789abcdef0123456789abcdef01234567', 'Bar',
                    '01 Baz.mp3']
        actual = target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_length_title(self):
        s = '0123456789abcdef' * 4
        tags = self._buildTags(title=s)
        expected = ['Foo', 'Bar',
                    '01 0123456789abcdef0123456789abcdef0.mp3']
        actual = target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_length_title_disc(self):
        s = '0123456789abcdef' * 4
        tags = self._buildTags(title=s, totalDisc=2)
        expected = ['Foo', 'Bar',
                    '01-01 0123456789abcdef0123456789abcd.mp3']
        actual = target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_matchExtension(self):
        tags = self._buildTags()
        expected = ['Foo', 'Bar', '01 Baz.MP3']
        actual = target.buildPath(tags, 'MP3')
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_trim_watchTrailingSpaces(self):
        tags = self._buildTags(
            title='0        9' * 4,
            album='We got it from Here... Thank You 4 Your service',
            albumArtist='0        9abcdef' * 4
        )
        expected = [
            '0        9abcdef0        9abcdef0',
            'We got it from Here___ Thank You 4 Your',
            '01 0        90        90        90.mp3'
        ]
        actual = target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_buildPath_trim(self):
        tags = self._buildTags(title=' B a z ', album=' B a r ',
                               albumArtist=' F o o ')
        expected = ['F o o', 'B a r', '01 B a z.mp3']
        actual = target.buildPath(tags)
        self.assertSequenceEqual(expected, actual)

    def test_imageFileName_badFileChars(self):
        self.data['album'] = 'On / Off'
        self.data['title'] = 'Baz:'
        actual = target.imageFileName(self.data, 'jpeg')
        self.assertEqual(actual, 'Bar - On _ Off - Baz.jpeg')

    def test_imageFileName_endsWithSpace(self):
        self.data['title'] = 'Baz  '
        actual = target.imageFileName(self.data, 'jpeg')
        self.assertEqual(actual, 'Bar - Foo - Baz.jpeg')

if __name__ == '__main__':
    unittest.main()
