from __future__ import unicode_literals
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
            'aggregations': {
                'primary': {
                    'buckets': [{
                        'key': 'foo',
                        'secondary': {
                            'buckets': [
                                {'key': 'bar'},
                                {'key': 'baz'}
                                ]
                        }
                    }]
                }
            }
        }

        actual = list(sut.findClones(client))
        self.assertEqual(client.search.call_count, 1)
        self.assertEqual(actual, [
            ('foo', 'bar'),
            ('foo', 'baz')
        ])


class TestFindIsonoms(unittest.TestCase):
    def setUp(self):
        self.fixture = {
            'album': 'Bar',
            'artist': 'Foo (with Qaz)',
            'track': 5,
            'totalTrack': 14,
            'compilation': None,
            'title': 'Baz',
            'albumArtist': 'Foo',
            'totalDisc': 1,
            'disc': 1,
            'id': 'barfoo'
        }
        self.qualityMatch = {
            'hits': {
                'hits': [{
                    '_score': 12.1,
                    '_source': {'foo': 'bar', 'path': '/path/to/foo'}
                }],
                'max_score': 12.1,
                'total': 9999
            }
        }

    def test_isonomQuery_empty(self):
        with self.assertRaises(ValueError):
            sut._isonomQuery({})

    def test_isonomQuery_missingTrackNumber(self):
        del self.fixture['track']
        actual = sut._isonomQuery(self.fixture)
        compound = actual['query']['bool']
        terms = json.dumps(compound['should'])
        self.assertIn('must_not', compound)
        self.assertIn('artist', terms)
        self.assertNotIn('track', terms)

    def test_isonomQuery_nullTrackNumber(self):
        self.fixture['track'] = None
        actual = sut._isonomQuery(self.fixture)
        compound = actual['query']['bool']
        terms = json.dumps(compound['should'])
        self.assertIn('must_not', compound)
        self.assertIn('artist', terms)
        self.assertNotIn('track', terms)

    def test_isonomQuery_missingTitle(self):
        del self.fixture['title']
        actual = sut._isonomQuery(self.fixture)
        compound = actual['query']['bool']
        terms = json.dumps(compound['should'])
        self.assertIn('must_not', compound)
        self.assertIn('track', terms)
        self.assertNotIn('title', terms)

    def test_isonomQuery_nullTitle(self):
        self.fixture['title'] = None
        actual = sut._isonomQuery(self.fixture)
        compound = actual['query']['bool']
        terms = json.dumps(compound['should'])
        self.assertIn('must_not', compound)
        self.assertIn('track', terms)
        self.assertNotIn('title', terms)

    def test_isonomQuery_missingAlbum(self):
        del self.fixture['album']
        actual = sut._isonomQuery(self.fixture)
        compound = actual['query']['bool']
        terms = json.dumps(compound['should'])
        self.assertIn('must_not', compound)
        self.assertIn('title', terms)
        self.assertNotIn('album', terms)

    def test_isonomQuery_emptyAlbum(self):
        self.fixture['album'] = ''
        actual = sut._isonomQuery(self.fixture)
        compound = actual['query']['bool']
        terms = json.dumps(compound['should'])
        self.assertIn('must_not', compound)
        self.assertIn('title', terms)
        self.assertNotIn('album', terms)

    def test_isonomQuery_missingArtist(self):
        del self.fixture['artist']
        actual = sut._isonomQuery(self.fixture)
        compound = actual['query']['bool']
        terms = json.dumps(compound['should'])
        self.assertIn('must_not', compound)
        self.assertIn('album', terms)
        self.assertNotIn('artist', terms)

    def test_isonomQuery_missingId(self):
        del self.fixture['id']
        actual = sut._isonomQuery(self.fixture)
        compound = actual['query']['bool']
        self.assertNotIn('must_not', compound)

    def test_isonomQuery_blankId(self):
        self.fixture['id'] = ''
        actual = sut._isonomQuery(self.fixture)
        compound = actual['query']['bool']
        self.assertNotIn('must_not', compound)

    @patch('pyTagger.operations.find_duplicates.Client', spec=True)
    def test_findIsonomTracks(self, client):
        client.search.return_value = self.qualityMatch
        gen = sut.findIsonomTracks(client, self.fixture)
        actual = list(gen)
        self.assertEqual(client.search.call_count, 1)
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0][0], "/path/to/foo")
        self.assertEqual(actual[0][1], 12.1)
        self.assertEqual(actual[0][2], {"foo": "bar"})

    @patch('pyTagger.operations.find_duplicates.Client', spec=True)
    def test_findIsonomsInsufficient(self, client):
        client.search.side_effect = ValueError
        gen = sut.findIsonoms(client, {'foo': self.fixture})
        actual = list(gen)
        self.assertEqual(client.search.call_count, 1)
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0].status, 'insufficient')

    @patch('pyTagger.operations.find_duplicates.Client', spec=True)
    def test_findIsonomsQualitySingle(self, client):
        client.search.return_value = self.qualityMatch
        gen = sut.findIsonoms(client, {'foo': self.fixture})
        actual = list(gen)
        self.assertEqual(client.search.call_count, 1)
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0].status, 'single')

    @patch('pyTagger.operations.find_duplicates.Client', spec=True)
    def test_findIsonomsSufficientSingle(self, client):
        client.search.return_value = {
            'hits': {
                'hits': [{
                    '_score': 8.1,
                    '_source': {'foo': 'bar', 'path': '/path/to/foo'}
                }],
                'max_score': 8.1,
                'total': 9999
            }
        }

        gen = sut.findIsonoms(client, {'foo': self.fixture})
        actual = list(gen)
        self.assertEqual(client.search.call_count, 1)
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0].status, 'single')

    @patch('pyTagger.operations.find_duplicates.Client', spec=True)
    def test_findIsonomsMultiple(self, client):
        client.search.return_value = {
            'hits': {
                'hits': [
                    {
                        '_score': 8.1,
                        '_source': {'foo': 'bar', 'path': '/path/to/foo'}
                    },
                    {
                        '_score': 8.1,
                        '_source': {'foo': 'bar', 'path': '/path/to/foo'}
                    },
                ],
                'max_score': 8.1,
                'total': 9999
            }
        }

        gen = sut.findIsonoms(client, {'foo': self.fixture})
        actual = list(gen)
        self.assertEqual(client.search.call_count, 1)
        self.assertEqual(len(actual), 2)
        self.assertEqual(actual[0].status, 'multiple')
        self.assertEqual(actual[1].status, 'multiple')

    @patch('pyTagger.operations.find_duplicates.Client', spec=True)
    def test_findIsonomsNone(self, client):
        client.search.return_value = {
            'hits': {
                'hits': [],
                'max_score': 0.0,
                'total': 9999
            }
        }

        gen = sut.findIsonoms(client, {'foo': self.fixture})
        actual = list(gen)
        self.assertEqual(client.search.call_count, 1)
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0].status, 'nothing')

if __name__ == '__main__':
    unittest.main()
