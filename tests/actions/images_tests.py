import unittest
import sys
import pyTagger.actions.images as target
from pyTagger.utils import configurationOptions
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestImagesAction(unittest.TestCase):
    def setUp(self):
        with patch.object(sys, 'argv', ['test', '/path/foo', '/path/bar']):
            self.options = configurationOptions('images')

    @patch('pyTagger.actions.images.ID3Proxy')
    @patch('pyTagger.actions.images.extractImages')
    @patch('pyTagger.actions.images.os')
    def test_process_directory(self, os, extractImages, id3Proxy):
        os.path.isfile.return_value = False
        os.path.isdir.return_value = True
        id3Proxy.return_value = 'id3Proxy'
        extractImages.return_value = 'passed'

        actual = target.process(self.options)

        self.assertEqual(id3Proxy.call_count, 1)
        extractImages.assert_called_once_with(
            '/path/foo', '/path/bar', 'id3Proxy'
        )
        self.assertEqual(actual, 'passed')

    @patch('pyTagger.actions.images.ID3Proxy')
    @patch('pyTagger.actions.images.extractImagesFrom')
    @patch('pyTagger.actions.images.os')
    def test_process_file(self, os, extractImages, id3Proxy):
        os.path.isfile.return_value = True
        id3Proxy.return_value = 'id3Proxy'
        extractImages.return_value = 'passed'

        actual = target.process(self.options)

        self.assertEqual(id3Proxy.call_count, 1)
        extractImages.assert_called_once_with(
            '/path/foo', '/path/bar', 'id3Proxy'
        )
        self.assertEqual(actual, 'passed')

    def test_process_unknown(self):
        with self.assertRaises(ValueError):
            actual = target.process(self.options)

if __name__ == '__main__':
    unittest.main()
