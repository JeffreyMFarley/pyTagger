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
        self.target = Client('foo', 'bar')
        self.snapshot = {'foo': {'bar': 'baz'}}

    def test_exists(self):
        self.target.exists()
        self.target.es.indices.exists.assert_called_once_with(index='foo')

    @patch('pyTagger.proxies.es.loadJson')
    def test_create(self, loadJson):
        data = {'baz': 'qaz'}
        loadJson.return_value = data

        self.target.create()

        loadJson.assert_called_once()
        self.target.es.indices.create.assert_called_once_with(
            index='foo', body=data
        )

    def test_load_happy(self):
        self.target.load(self.snapshot)

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
        self.target.load(self.snapshot)
        self.target.create.assert_called_once()

    def test_load_create_fails(self):
        with self.assertRaises(Exception):
            self.target.exists = Mock(return_value=False)
            self.target.create = Mock(return_value=False)
            self.target.load(self.snapshot)

    def test_load_bad_document(self):
        self.target.es.create = Mock(side_effect=RequestError)
        with self.assertRaises(IndexError):
            self.target.load(self.snapshot)

if __name__ == '__main__':
    unittest.main()
