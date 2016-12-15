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
    def test_process_directory(self, extractImages, id3Proxy):
        id3Proxy.return_value = 'id3Proxy'
        extractImages.return_value = 'passed'

        actual = target.process(self.options)

        self.assertEqual(id3Proxy.call_count, 1)
        extractImages.assert_called_once_with(
            '/path/foo', '/path/bar', 'id3Proxy'
        )
        self.assertEqual(actual, 'passed')

if __name__ == '__main__':
    unittest.main()
