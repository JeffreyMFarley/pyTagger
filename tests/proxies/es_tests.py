import unittest
from pyTagger.proxies.es import Client
from elasticsearch import ConnectionError, RequestError
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


class TestElasticsearchClient(unittest.TestCase):
    @patch('pyTagger.proxies.es.Elasticsearch')
    def setUp(self, elasticsearch):
        import sys
        args = ['test', '--es-index', 'foo', '--es-type', 'bar']
        with patch.object(sys, 'argv', args):
            self.target = Client()
            self.target.es.create = Mock(return_value={'created': True})
            self.snapshot = {'foo': {'bar': 'baz'}}

    def test_exists(self):
        self.target.exists()
        self.target.es.indices.exists.assert_called_once_with(index='foo')

    @patch('pyTagger.proxies.es.loadJson')
    def test_create(self, loadJson):
        data = {'baz': 'qaz'}
        loadJson.return_value = data

        self.target.create()

        self.assertEqual(loadJson.call_count, 1)
        self.target.es.indices.create.assert_called_once_with(
            index='foo', body=data
        )

    def test_load_happy(self):
        data = {k: {'baz': 'qaz'} for k in range(1, 1002)}
        actual = self.target.load(data)
        self.assertEqual(actual, (1001, 0))

    def test_load_null_input(self):
        with self.assertRaises(TypeError):
            self.target.load(None)

    def test_load_string_input(self):
        with self.assertRaises(TypeError):
            self.target.load('foo')

    def test_load_not_connected(self):
        self.target.es.indices.exists = Mock(side_effect=ConnectionError)
        with self.assertRaises(ConnectionError):
            self.target.load(self.snapshot)

    def test_load_when_not_exists(self):
        self.target.exists = Mock(return_value=False)
        self.target.create = Mock(return_value=True)
        actual = self.target.load(self.snapshot)
        self.assertEqual(self.target.create.call_count, 1)
        self.assertEqual(actual, (1, 0))

    def test_load_create_fails(self):
        with self.assertRaises(Exception):
            self.target.exists = Mock(return_value=False)
            self.target.create = Mock(return_value=False)
            self.target.load(self.snapshot)

    def test_load_bad_document(self):
        def raiseRequestError(*args, **kwargs):
            raise RequestError(400, 'error', {'a': 'b'})

        self.target.es.create = Mock(side_effect=raiseRequestError)
        actual = self.target.load(self.snapshot)
        self.assertEqual(actual, (0, 1))

    def test_load_ufid_has_dots(self):
        data = {
            'foo': {
                'ufid': {'http://musicbrainz.org': 'bar'}
            }
        }
        actual = self.target.load(data)
        self.assertEqual(actual, (1, 0))
        self.target.es.create.assert_called_once_with(
            index='foo', doc_type='bar', body={
                'path': 'foo',
                'ufid': {'http://musicbrainz_org': 'bar'}
            }
        )

    def test_replaceDots(self):
        data = {
            'abdef': 'ghijkl',
            'a.b.c': 'mnopqr'
        }
        actual = self.target._replaceDots(data)
        self.assertEqual(actual, {
            'abdef': 'ghijkl',
            'a_b_c': 'mnopqr'
        })

    def test_search(self):
        expected = {'foo': 'bar'}
        data = {'baz': 'qaz'}
        self.target.es.search = Mock(return_value=expected)

        actual = self.target.search(data)
        self.assertEqual(actual, expected)
        self.target.es.search.assert_called_once_with(
            index='foo', doc_type='bar', body=data
        )

    def test_delete(self):
        self.target.es.indices.delete = Mock(return_value={
            'acknowledged': True
        })

        actual = self.target.delete()
        self.target.es.indices.delete.assert_called_once_with(
            index='foo'
        )

if __name__ == '__main__':
    unittest.main()
