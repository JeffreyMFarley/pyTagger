import sys
import unittest
import pickle
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from pyTagger.proxies.echonest import EchoNestProxy


# 'Echonest API has deprecated and moved to Spotify 2016-05'
@unittest.skipIf(sys.version >= '3', 'The pickle files work with Python 2')
class Test_EchoNestProxy(unittest.TestCase):
    fields = {'artist', 'title', 'key', 'length', 'bpm',
              'id_musicbrainz_artist', 'id_musicbrainz_song',
              'id_echonest_artist', 'id_echonest_song',
              'acousticness', 'danceability', 'energy', 'instrumentalness',
              'liveness', 'loudness', 'speechiness', 'valence'
              }

    def setUp(self):
        import sys
        args = ['test', '--echonest-api-key', 'foobarbazqaz']
        with patch.object(sys, 'argv', args):
            self.target = EchoNestProxy()

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def to_absolute(self, fileName):
        import os.path
        # where is this module?
        thisDir = os.path.dirname(__file__)
        return os.path.join(thisDir, fileName)

    def load(self, shortName):
        fileName = self.to_absolute('echonest-' + shortName + '.p')
        with open(fileName, 'rb') as f:
            return pickle.load(f)

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    @patch('pyTagger.proxies.echonest.requests')
    def test_offline(self, requests):
        r = self.load('simple')
        r.status_code = 404
        requests.get.return_value = r

        actual = list(self.target.getByArtist(u'Foo'))

        self.assertIsNotNone(actual)
        self.assertEqual(1, requests.get.call_count)
        self.assertEqual(0, len(actual))

    @patch('pyTagger.proxies.echonest.requests')
    def test_rateLimit(self, requests):
        r = self.load('rateLimit')
        requests.get.return_value = r

        actual = list(self.target.getByArtist(u'Foo'))

        self.assertIsNotNone(actual)
        self.assertEqual(1, requests.get.call_count)
        self.assertEqual(0, len(actual))
        self.assertEqual(429, self.target.status_code)

    @patch('pyTagger.proxies.echonest.requests')
    def test_tooManyResults(self, requests):
        r = self.load('tooManyResults')
        requests.get.return_value = r

        actual = list(self.target.getByArtist(u'Foo'))

        self.assertIsNotNone(actual)
        self.assertEqual(1, requests.get.call_count)
        self.assertEqual(0, len(actual))
        self.assertEqual(400, self.target.status_code)

    @patch('pyTagger.proxies.echonest.requests')
    def test_getByArtist_simple(self, requests):
        r = self.load('simple')
        requests.get.return_value = r

        actual = list(self.target.getByArtist(u'Foo'))

        self.assertIsNotNone(actual)
        self.assertEqual(1, requests.get.call_count)
        self.assertEqual(59, len(actual))
        for song in actual:
            self.assertEqual(self.fields, set(song.keys()))
            self.assertIn('Die Antwoord', song['artist'])

    @patch('pyTagger.proxies.echonest.requests')
    def test_getByArtist_multiple(self, requests):
        def side_effect(*args, **kwargs):
            offset = str(kwargs['params']['start'])
            return self.load('chunks-' + offset)

        requests.get.side_effect = side_effect

        actual = list(self.target.getByArtist(u'Foo'))

        self.assertIsNotNone(actual)
        self.assertEqual(3, requests.get.call_count)
        self.assertEqual(239, len(actual))
        for song in actual:
            self.assertEqual(self.fields, set(song.keys()))
            self.assertIn('Meat Beat Manifesto', song['artist'])

if __name__ == '__main__':
    unittest.main()
