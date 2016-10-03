import unittest
import json
import pyTagger.operations.find_duplicates as sut
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


class TestFindClones(unittest.TestCase):
    @patch('pyTagger.operations.find_duplicates.Client', spec=True)
    def test_findClones(self, client):
        client.search.return_value = {
            u'aggregations': {
                u'primary': {
                    u'buckets': [{
                        u'key': u'foo',
                        u'secondary': {
                            u'buckets': [
                                {u'key': u'bar'},
                                {u'key': u'baz'},
                            ]
                        }
                    }]
                }
            }
        }

        actual = list(sut.findClones(client))
        self.assertEqual(client.search.call_count, 1)
        self.assertEqual(actual, [
            (u'foo', u'bar'),
            (u'foo', u'baz')
        ])


class TestFindIsonoms(unittest.TestCase):
    def setUp(self):
        self.fixture = {
            'album': u'Bar',
            'artist': u'Foo (with Qaz)',
            'track': 5,
            'totalTrack': 14,
            'compilation': None,
            'title': u'Baz',
            'albumArtist': u'Foo',
            'totalDisc': 1,
            'disc': 1
        }

    def test_isonomQuery_empty(self):
        with self.assertRaises(ValueError):
            sut._isonomQuery({})

    def test_isonomQuery_missingTrackNumber(self):
        del self.fixture['track']
        actual = sut._isonomQuery(self.fixture)
        terms = json.dumps(actual['query']['bool']['should'])
        self.assertIn('artist', terms)
        self.assertNotIn('track', terms)

    def test_isonomQuery_nullTrackNumber(self):
        self.fixture['track'] = None
        actual = sut._isonomQuery(self.fixture)
        terms = json.dumps(actual['query']['bool']['should'])
        self.assertIn('artist', terms)
        self.assertNotIn('track', terms)

    def test_isonomQuery_missingTitle(self):
        del self.fixture['title']
        actual = sut._isonomQuery(self.fixture)
        terms = json.dumps(actual['query']['bool']['should'])
        self.assertIn('track', terms)
        self.assertNotIn('title', terms)

    def test_isonomQuery_nullTitle(self):
        self.fixture['title'] = None
        actual = sut._isonomQuery(self.fixture)
        terms = json.dumps(actual['query']['bool']['should'])
        self.assertIn('track', terms)
        self.assertNotIn('title', terms)

    def test_isonomQuery_missingAlbum(self):
        del self.fixture['album']
        actual = sut._isonomQuery(self.fixture)
        terms = json.dumps(actual['query']['bool']['should'])
        self.assertIn('title', terms)
        self.assertNotIn('album', terms)

    def test_isonomQuery_emptyAlbum(self):
        self.fixture['album'] = ''
        actual = sut._isonomQuery(self.fixture)
        terms = json.dumps(actual['query']['bool']['should'])
        self.assertIn('title', terms)
        self.assertNotIn('album', terms)

    def test_isonomQuery_missingArtist(self):
        del self.fixture['artist']
        actual = sut._isonomQuery(self.fixture)
        terms = json.dumps(actual['query']['bool']['should'])
        self.assertIn('album', terms)
        self.assertNotIn('artist', terms)

    @patch('pyTagger.operations.find_duplicates.Client', spec=True)
    def test_findIsonomTracks(self, client):
        client.search.return_value = {
            "hits": {
                "hits": [{
                    "_score": 10.1,
                    "_source": {"foo": "bar"}
                }],
                "max_score": 10.1,
                "total": 9999
            }
        }

        gen = sut.findIsonomTracks(client, self.fixture)
        actual = list(gen)
        self.assertEqual(client.search.call_count, 1)
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0][0], self.fixture)
        self.assertEqual(actual[0][1], 10.1)
        self.assertEqual(actual[0][2], {"foo": "bar"})

if __name__ == '__main__':
    unittest.main()
