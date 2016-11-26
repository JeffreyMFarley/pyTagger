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

    def test_imageFileName_badFileChars(self):
        self.data['album'] = 'On / Off'
        actual = target.imageFileName(self.data, 'jpeg')
        self.assertEqual(actual, 'Bar - On _ Off - Baz.jpeg')

if __name__ == '__main__':
    unittest.main()
