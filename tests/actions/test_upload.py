import unittest
import pyTagger.actions.upload as target
from pyTagger.utils import configurationOptions
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


class TestElasticsearchClient(unittest.TestCase):
    def setUp(self):
        self.snapshot = {'foo': 'bar'}
        self.options = configurationOptions('upload')

    @patch('pyTagger.actions.upload.Client')
    @patch('pyTagger.actions.upload.loadJson')
    def test_uploadToElasticsearch_happy(self, loadJson, es_module):
        client = es_module.return_value
        client.exists.return_value = False
        client.load.return_value = (1, 0)

        loadJson.return_value = self.snapshot

        actual = target.uploadToElasticsearch(self.options)

        loadJson.assert_called_once_with(self.options.library_snapshot)
        self.assertEqual(client.exists.call_count, 1)
        client.load.assert_called_once_with(self.snapshot)
        self.assertEqual(actual, 'Loaded 1 records\nFailed 0')

    @patch('pyTagger.actions.upload.Client')
    @patch('pyTagger.actions.upload.loadJson')
    def test_uploadToElasticsearch_reload(self, loadJson, es_module):
        client = es_module.return_value
        client.exists.return_value = True
        client.load.return_value = (1, 0)

        loadJson.return_value = self.snapshot

        self.options.reload = True

        actual = target.uploadToElasticsearch(self.options)

        self.assertEqual(client.exists.call_count, 1)
        self.assertEqual(client.delete.call_count, 1)
        client.load.assert_called_once_with(self.snapshot)
        self.assertEqual(actual, 'Loaded 1 records\nFailed 0')

    @patch('pyTagger.actions.upload.Client')
    @patch('pyTagger.actions.upload.loadJson')
    def test_uploadToElasticsearch_append(self, loadJson, es_module):
        client = es_module.return_value
        client.exists.return_value = True
        client.load.return_value = (1, 0)

        loadJson.return_value = self.snapshot

        self.options.append = True

        actual = target.uploadToElasticsearch(self.options)

        self.assertEqual(client.exists.call_count, 1)
        self.assertEqual(client.delete.call_count, 0)
        client.load.assert_called_once_with(self.snapshot)
        self.assertEqual(actual, 'Loaded 1 records\nFailed 0')

    @patch('pyTagger.actions.upload.Client')
    @patch('pyTagger.actions.upload.loadJson')
    def test_uploadToElasticsearch_no_overwrite(self, loadJson, es_module):
        client = es_module.return_value
        client.exists.return_value = True

        loadJson.return_value = self.snapshot

        with self.assertRaises(ValueError):
            actual = target.uploadToElasticsearch(self.options)

    @patch('pyTagger.actions.upload.Client')
    @patch('pyTagger.actions.upload.loadJson')
    def test_uploadToElasticsearch_no_file(self, loadJson, es_module):
        client = es_module.return_value
        loadJson.side_effect = IOError

        with self.assertRaises(IOError):
            actual = target.uploadToElasticsearch(self.options)

        self.assertEqual(client.exists.call_count, 0)

if __name__ == '__main__':
    unittest.main()
